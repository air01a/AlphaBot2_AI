import boto3 def lambda_handler(event, context):
	client = boto3.client('rekognition')
	bucket = "xxxxxxx-faces"
	for rec in event['Records']:
		if 's3' in rec.keys():
			file = rec['s3']['object']['key']
			name = file.split('.')[0].split('_')[0]
			response = client.index_faces(ExternalImageId=name,Image={"S3Object": {"Bucket": bucket,"Name":file}}, CollectionId="BETTERAVE_FACES")


