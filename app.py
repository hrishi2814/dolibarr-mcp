import gradio as gr

def letter_counter(word, letter):
    """
    Counts the number of occurences of a letter in a word or text.

    Args:
        word (str): The word or text to count the letter in.
        letter (str): The letter to count.

    Returns:
            int: The number of occurences of the letter in the word or text.
    """
    word = word.lower()
    letter = letter.lower()
    count = word.count(letter)
    return count

demo = gr.Interface(
    fn=letter_counter,
    inputs=[gr.Textbox("strawberry"), gr.Textbox("r")],
    outputs=[gr.Number()],
    title="Letter Counter",
    description="Enter a word or text and a letter to count the number of occurences of the letter in the word or text.",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)