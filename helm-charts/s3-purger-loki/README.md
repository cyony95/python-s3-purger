#s3-purger-loki helm chart

This chart has a python script that checks some watermarks(98 to 95%) and deletes oldest files in an s3 bucket for Loki. A contingency plan.