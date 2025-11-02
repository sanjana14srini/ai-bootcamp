1. 
https://github.com/sanjana14srini/ai-bootcamp/blob/main/capstone_project/project.py

2. Chunking strategy for project:
The task of this project is to be read in research papers from arxiv and build agent(s) that can answer questions about these papers, 
summarize the main research in these papers, compare multiple papers and write a literature review based on the findings. 
For this we will need to correctly parse and chunk the data within the research papers. A chunking strategy is necessary because research
papers tend to be multiple pages long with different sections. After carefully evaluating different chunking approaches, I have decided to go 
ahead with the sliding window approach for the time being. The other candidates were paragraph chunking, section based chunking,
and intelligent chunking using LLM. Since research papers have an inherent structure associated with them, parahraph chunking would not be the ideal choice, 
as it won't take this structure into account. Chunking using LLM would be prohibitively expensive in chunking documents as large as research papers. 
Section based chunking is definitely the better choice to be taken here owing to the inherent structure within research papers. Frameworks such as PyMuPDF can be used to achieve this. 
However this is a bit complicated to implement and requires more thought. The complexity not only arises from the implementation of this python package,
but also from the perspective of diversity in research paper structures. Although research papers follow a similar structure at a high level, different papers
have different internal structuring - such as including or excluding sections for Discussion, Future Work, Examples etc. These nuances will disrupt in
capturing all possible paper structures. 
Taking these complexeties into consideration, the easiest to implement at this point would be a sliding window chunking approach. 
This should easily capture all text data, however it will fail in extracting tables and images which PyMuPDF could help mitigate. 
If we view from the perspective of what we are trying to accomplish with the agent, then we are limited to working with only text. Agents that we will work with
are primarily only text-based models. Even if we want to process images or tables, these would need to first be converted into meaningful text. 
Having this would definitely be a nice add on, that packages like PyMuPDF can achieve. But for the sake of this project, this would a be secondary goal 
to achieve. In any case, this chunking choice is preliminary and ultimately I will choose the final chunking strategy in a data-driven way.

I am working with a chunk size of 5000 with a step size of 1000 to meaninfully capture the volume of the research paper with some overlap. However, it
is hard to justify that this chunk size will work for all cases since research papers highly differ in size. Some research papers are only 8 pages long, whereas
some others can be as long as 20 pages. The depth that each research paper gets into would also be highly varying. So the chunk and step sizes are based on 
a high level estimate on the size of research papers. I would need to iterate over different values to see what ultimately works well across different cases.


3. Persistent vs. In-memory storage
Data from research papers are very bulky and dense in nature, and therefore storing them in-memory can make processes very slow and expensive. 
For this reason, I would like to work with a persistent memory storage. Among all choices present, Elasticsearch seems to be the best choice. Although it 
is not meant to work at scale with LLM Agents ike Qdrant or faiss, it suits the needs of this project because it provides hybrid search functionality. 
This is important for our case because we need the agent to provide robust search functionalities when searching through vast arrays of text data that 
are already semantically similar. For instance, if as a user I want to build a literature review on all the research so far on LoRA, then the data that we
will be working with will already be very semantically similar as it will be restricted to this specific topic. In situations like this, having keyword based
search along with vector search will help make searching more robust. 




4. 
Framework: Pydantic AI 
LLM Provider: OpenAI



5. 
Instructions for the orchestrator agent
orchestrator_instructions = """
Your task is to help the user by answering their questions
about wikipedia pages.

If a user query has NO web url, then use ONLY the search tool. 

In order to fetch the wikipedia page, use the fetch_web_page tool. 
The whole function needs to be run in order to get the webpage content.

Always generate summaries of the webpages using the summarization agent 

If a user query has NO web url, then use ONLY the search tool. 

No need to save summary when using the search tool.
Always save summary when using the fetch_web_page tool.

""".strip()


Instructions for the summarizing agent
summarizing_instructions = """
    You are a helpful assistant that summarizes Wikipedia articles.
""".strip()




6. 
--- Function Call ---
Function: search
Arguments: "{\"query\":\"threats to capybara populations\"}


Assistant: Capybara populations face several threats, including:

1. **Hunting**: Capybaras are hunted for their meat and hides in some areas of South America. This hunting pressure can lead to localized declines in their populations.

2. **Habitat Loss**: Deforestation and conversion of wetlands for agriculture or urban development reduce available habitats for capybaras. As they depend on dense vegetation near water bodies, habitat destruction impacts their survival.

3. **Competition with Livestock**: Farmers sometimes consider capybaras to be competitors for grazing resources. This perception can lead to intentional killings or control measures against them.

4. **Urbanization**: As human populations expand into capybara habitats, they may experience increased human-wildlife conflict. Capybaras may be displaced from their natural environments, leading to stresses on their populations.

5. **Ecosystem Changes**: Climate change and alterations to waterways can also affect capybara habitats and food sources, posing additional threats to their survival.

Despite these challenges, capybara populations are currently stable in many parts of their range, although local populations can fluctuate based on specific environmental and human factors.