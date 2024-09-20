This project leverages openai's gpt-4o to parse images of pdfs.

There is one sample pdf available in the project, named sample.pdf. This sample pdf is taken from the fidelity website.

When the user hits the enfpoint `/pdf_viewer/{pdf_name}` the full pdf will be rendered in a webpage.
`http://localhost:8000/pdf_viewer/sample`

To pre-process the pdf so that we only convert relevant files to images, there is a `/pdf_viewer/process` endpoint. This endpoint takes all pdfs in the source_pdfs directory and converts only relevant pages to images.


`http://localhost:8000/pdf_viewer/process`


To see json output of the extractions:

`http://localhost:8000/extractions/sample`

Techniques:

The first step in the process is to page-by-page ask openai to summarize the contents of a range of pages. If the contents are relevant to the extraction, as in if there are words that appear to be related to account holder, account value, or holdings, then the result of the summary is captured as part of the conversation history, and the next page is processed. After all pages are processed and converted into Json, pydantic is used to form a structured response from the Json output. This gives us a summary of said range where we discard extra historical info.

The second step in the process is to create prompts that are targetd towards holdings or account summary. 
