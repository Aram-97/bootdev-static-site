from textnode import BlockType, TextType, TextNode
from htmlnode import LeafNode, ParentNode, HTMLNode
import re


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode("", text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url or ""})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url or "", "alt": text_node.text})
    else:
        raise Exception("Unknown text type!")


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        delimeter_count = node.text.count(delimiter)

        if delimeter_count % 2 != 0:
            raise Exception("Invalid Markdown syntax!")

        node_chunks = node.text.split(delimiter)

        while delimeter_count >= 0:
            chunk = node_chunks.pop(0)

            if chunk != "":
                new_nodes.append(
                    TextNode(
                        chunk, TextType.TEXT if delimeter_count % 2 == 0 else text_type
                    )
                )

            delimeter_count = delimeter_count - 1

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]+)\]\(([^()]+)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!\!)\[([^\[\]]+)\]\(([^()]+)\)", text)


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)

        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    text_nodes: list[TextNode] = [TextNode(text, TextType.TEXT)]

    for text_type in TextType:
        match text_type:
            case TextType.BOLD:
                text_nodes = split_nodes_delimiter(text_nodes, "**", text_type)
                continue
            case TextType.ITALIC:
                text_nodes = split_nodes_delimiter(text_nodes, "_", text_type)
                continue
            case TextType.CODE:
                text_nodes = split_nodes_delimiter(text_nodes, "`", text_type)
                continue
            case TextType.LINK:
                text_nodes = split_nodes_link(text_nodes)
                continue
            case TextType.IMAGE:
                text_nodes = split_nodes_image(text_nodes)
                continue

    return text_nodes


def markdown_to_blocks(markdown: str):
    splitted_blocks = markdown.split("\n\n")
    stripped_blocks = map(lambda block: block.strip(), splitted_blocks)
    return list(filter(lambda block: block != "", stripped_blocks))


def block_to_block_type(block: str):
    lines = block.split("\n")

    if re.match(r"^#{1,6}\s.+", block) != None:
        return BlockType.HEADING
    if re.match(r"^```\n[\s\S]+\n```$", block) != None:
        return BlockType.CODE
    if all(re.match(r"^>[^>]*", line) for line in lines):
        return BlockType.QUOTE
    if all(re.match(r"^-\s.+", line) for line in lines):
        return BlockType.UNORDERED_LIST
    if all(re.match(r"^\d+\.\s.+", line) for line in lines):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def block_type_to_html_node(block_type: BlockType, block: str) -> ParentNode | None:
    def build_children(text: str):
        return list(
            map(lambda node: text_node_to_html_node(node), text_to_textnodes(text))
        )

    if block_type == BlockType.PARAGRAPH:
        return ParentNode("p", build_children(block.replace("\n", " ")))
    elif block_type == BlockType.HEADING:
        matched = re.match(r"^(#{1,6})\s(.+)", block)

        if not matched:
            return None

        heading_type = matched.group(1)
        heading_text = matched.group(2)
        return ParentNode(f"h{len(heading_type)}", build_children(heading_text))
    elif block_type == BlockType.CODE:
        matched = re.match(r"^```\n([\s\S]+)\n```$", block)

        if not matched:
            return None

        content = matched.group(1)
        return ParentNode("pre", [LeafNode("code", content)])
    elif block_type == BlockType.QUOTE:
        lines = block.split("\n")
        lines_content = map(lambda line: line[1:].strip(), lines)
        return ParentNode("blockquote", build_children("\n".join(lines_content)))
    elif block_type == BlockType.UNORDERED_LIST:
        lines = block.split("\n")
        built_children = map(
            lambda line: ParentNode("li", build_children(line[1:].strip())), lines
        )
        return ParentNode("ul", list(built_children))
    elif block_type == BlockType.ORDERED_LIST:
        lines = block.split("\n")
        built_children = map(
            lambda line: ParentNode(
                "li", build_children(re.match(r"^\d\.\s(.+)", line).group(1))
            ),
            lines,
        )
        return ParentNode("ol", list(built_children))
    else:
        raise Exception("Unknown text type!")


def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown)
    html_nodes = []

    for block in blocks:
        block_type = block_to_block_type(block)
        html_nodes.append(block_type_to_html_node(block_type, block))

    return ParentNode("div", html_nodes)


def extract_title(markdown: str) -> str:
    h1_heading = re.match(r"^#\s(.+)", markdown)

    if h1_heading is None:
        raise Exception("Heading 1 not found")

    return h1_heading.group(1)
