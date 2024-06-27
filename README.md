
I chose to take in a source directory where pdf files will be uploaded by the user. If a user uploads to the source_pdfs directory, then the name of the pdf will be used to create a namespace in the /media folder. Only relevant pages will be converted into pngs.

To render the full pdf in a viewer:

http://localhost:8000/pdf_viewer/sample

To convert relevant pdfs into images for extraction:

http://localhost:8000/pdf_viewer/process


To see json output of the extractions:

http://localhost:8000/extractions/sample