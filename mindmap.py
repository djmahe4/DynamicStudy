from google import genai
import os
import random
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from pylatexenc.latex2text import LatexNodes2Text
from google.genai import types
import textwrap


def build_graph(nested_dict, G=None, parent=None, depth=0):
    if G is None:
        G = nx.DiGraph()
    for key, value in nested_dict.items():
        G.add_node(key, depth=depth)
        if parent is not None:
            G.add_edge(parent, key)
        build_graph(value, G, parent=key, depth=depth + 1)
    return G


def create_mindmap(nested_dict, output_filename="mindmap.jpg"):
    # Create graph and calculate depths
    G = build_graph(nested_dict)
    node_depths = nx.get_node_attributes(G, 'depth')
    max_depth = max(node_depths.values())

    # Create hierarchical layout
    shells = [[node for node, d in node_depths.items() if d == depth]
              for depth in range(max_depth + 1)]
    pos = nx.shell_layout(G, nlist=shells, scale=100)

    # Generate color palette
    palette = sns.color_palette("husl", n_colors=max_depth + 1)

    # Create figure
    fig, ax = plt.subplots(figsize=(40, 40))

    # Draw edges with arrows
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True,
                           arrowstyle='-|>', arrowsize=25,
                           connectionstyle="arc3,rad=0.1")

    # Draw nodes with wrapped text and styling
    for node in G.nodes():
        x, y = pos[node]
        depth = node_depths[node]

        # Text wrapping with line breaks
        wrapped_text = '\n'.join(textwrap.wrap(node, width=25))

        # Style parameters
        node_color = palette[depth]
        font_size = 22 - depth * 2
        font_size = max(font_size, 10)

        # Create text element with styled box
        ax.text(x, y, wrapped_text,
                ha='center', va='center',
                fontsize=font_size,
                bbox=dict(boxstyle="round,pad=0.4",
                          facecolor=node_color,
                          edgecolor="black",
                          linewidth=1.5))

    plt.axis('off')
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    #plt.close()

    return output_filename

def parse_mindmap_text(chat):
    """
    Parses a text-based mind map (using leading asterisks for hierarchy)
    into a nested dictionary.

    Args:
        chat: A string containing the mind map text.

    Returns:
        A dictionary representing the mind map structure.
    """
    lines = chat.strip().split("\n")
    root = {}
    stack = [root]
    prev_level = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith("```") or line.startswith("#"):
            continue

        level = 0
        for char in line:
            if char == "*":
                level += 1
            elif char==" ":
                continue
            else:
                break
        content = line[level:].strip()
        if ":" in content:
            x=content.split(":")
            if x[-1]=="":
                content=content
            else:
                content=x[-1][1:]
        if level > prev_level:
            # Going deeper, add a new dictionary to the last item in the stack
            if stack and content not in stack[-1]:
                stack[-1][content] = {}
                stack.append(stack[-1][content])
            elif stack and content in stack[-1]:
                stack.append(stack[-1][content]) # Handle cases where the same level appears again
        elif level == prev_level:
            # Staying at the same level, add a new item to the current dictionary
            if stack:
                stack[-2][content] = {} # Parent is the second to last in the stack
                stack[-1] = stack[-2][content] # Update the current level
        elif level < prev_level:
            # Going up a level, adjust the stack
            diff = prev_level - level
            for _ in range(diff):
                if len(stack) > 1:
                    stack.pop()
            if stack:
                stack[-1][content] = {}
                stack.append(stack[-1][content])
            elif not root and content: # Handle the case where we go back to the root
                root[content] = {}
                stack = [root, root[content]]


        prev_level = level

    return root

def generate_mind_text(client, prompt="page replacement techniques"):
    """
    Generates a detailed mindmap in Markdown format using the provided prompt.
    The guidelines are:
    1. Use `*` for the main heading (central topic).
    2. Use `>` for sub headings.
    3. Use `!` for points or sub-points.
    4. The main title must be exactly the prompt that the user enters.
    5. Ensure hierarchical indentation suitable for programmatic parsing.
    6. Avoid markdown images or non-text elements.
    """
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Generate a simple mindmap in Markdown format for the topic "[{prompt}]". 
                give the output as text with correct order with each point represented as * and the sub points have more 
                number of '*'s without spaces"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    a = "".join(item.text for item in
                client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config))
    #return a
    st.markdown(a)
    root = parse_mindmap_text(a)
    ax = create_mindmap(root)
    return ax

def generate_mindmap_data(query):
    """
    Generates mind map data from a query using a provided text generation function,
    using symbols for hierarchy:
      *  -> Main topic (which is exactly the query)
      >  -> Sub headings
      !  -> Points or sub-points

    Args:
        query (str): The topic for the mind map.

    Returns:
        tuple: A tuple containing the NetworkX DiGraph and a dictionary of nodes by type,
               or (None, None) if text generation fails or the result is invalid.
    """
    if st.button("Generate Mind Map"):
        if not query:
            st.warning("Please enter a topic")
        else:
            fig = generate_mind_text(st.session_state.client, query)
            if fig:
                st.pyplot(fig)
                st.success("Mind map generated successfully!")

                # Add download button
                from io import BytesIO
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
                buf.seek(0)
                st.download_button(
                    label="Download Mind Map",
                    data=buf,
                    file_name=f"{query}_mindmap.png",
                    mime="image/png"
                )
            else:
                st.error("Failed to generate mind map. Please check your API key and try again.")


    # response = generate_mind_text(st.session_state.client, query)
    # root=parse_mindmap_text(response)
    # output_file = create_mindmap(root)
    # print(f"Mindmap saved as {output_file}")
