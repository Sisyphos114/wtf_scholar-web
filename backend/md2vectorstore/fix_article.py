import os
from langchain_community.chat_models import ChatPerplexity

prompt = """
You are given the following article which discusses various aspects of mRNA vaccines for the African Swine Flu.

'''
{article}
'''

Modify the article so that the sections are according to the following outline. Change the text of the article as needed while maintaining coherence and consistency.

'''
{outline}
'''

Give your output below:
"""


def improve_article(llm):
    with open("article.txt", "r") as f:
        article = f.read()
    with open("outline.txt", "r") as f:
        outline = f.read()
    for i in range(3):
        print(f"Iteration {i+1}/3")
        response = llm.invoke(prompt.format(outline=outline, article=article))
        outputext = response.content
        outputfilename = f'output{i}.txt'
        with open(outputfilename, "w") as f:
             f.write(outputext)
        article = outputext


if __name__ == "__main__":
    model = "llama-3.1-sonar-huge-128k-online"
    llm = ChatPerplexity(api_key=os.environ["PPLX_API_KEY"], temperature=0, model=model)
    improve_article(llm)

