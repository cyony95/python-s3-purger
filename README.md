# python-s3-purger
An S3 purger that deletes files based on their timestamp until a certain free percentage is reached on the S3 bucket

It requires 5 env variables that you can set in values.yaml
- name: ACCESS_KEY
  value: {{ .Values.s3.access_key }}
- name: SECRET_KEY
  value: {{ .Values.s3.secret_key }}
- name: S3_ENDPOINT_URL
  value: {{ .Values.s3.url }}
- name: BUCKET_NAME
  value: {{ .Values.s3.bucket_name }}
- name: BUCKET_SIZE
  value: {{ .Values.s3.bucket_size }}       

There s also an unused function in the python code, that connects to prometheus and calculates the bucket size automatically from a netapp ontap metric. It s disabled for now, but if you have such metrics in prometheus, feel free to use the function but dont forget to change the metric variable.
