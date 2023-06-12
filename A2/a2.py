import grpc
from concurrent import futures
import os
from pathlib import Path
import boto3

import computeandstorage_pb2 as cs_pb2
import computeandstorage_pb2_grpc as cs_pb2_grpc

PORT = int(os.environ.get('PORT', 8000))
HOST = os.environ.get('HOST', '127.0.0.1')
file_path = "file.txt"

# Add your AWS credentials here
aws_access_key_id = 'ASIAXQKHQKQC6WBOQCUR'
aws_secret_access_key = 'k61jS7kv2YJjHyaFQFdOoDoaySXH2mLXrpLYjIKM'
aws_session_token = "FwoGZXIvYXdzEHgaDKfvOXUNOnsszNpktiLAAQ+3lK/X5p4AusbP6NaKkrwUHxHbUOMJ/CXaNKjHxLdqvaf1360+/vPRyBCn6MoW8p/LXURZSyYhcWAfLirY7rCvybE0Bu1KwsPK9FfB4GwuOwX+qtX88wgNILSXfd3yzJxxlpDC+252PJTw7U0tvnSWsCRwtX+1knyNvuZ2qBrBhilKA8MlpVj1KN9pV/O1ThktG/vjg/5AaYAn6a6out665UvAnfqZ4QAanft1qAR6XdQLDuxOhGhpXkyEq5E4KSii65OkBjItGFlq3kF4M1X+Nj4lUWSLmfjw5fQDKNrEjwYr1gsI3MH1gm4FOgaZr5ss9QEn"
region_name = 'us-east-1'

s3 = boto3.client(
    's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
    region_name=region_name
)
bucket_name = "grpc-data-bucket-rutvik-shah-2"

class EC2OperationsServicer(cs_pb2_grpc.EC2OperationsServicer):
    def StoreData(self, request, context):
        data = request.data
        try:
            with open(file_path, 'w') as file:
                file.write(data)
            with open(file_path, 'rb') as file:
                
                s3.upload_fileobj(file, bucket_name, file_path)
                
            print("test here")
            response = cs_pb2.StoreReply(s3uri=f"https://{bucket_name}.s3.amazonaws.com/{file_path}")
            return response

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)  # Set error code
            context.set_details("Error in storing data.")
            return cs_pb2.StoreReply()

    def AppendData(self, request, context):
        data = request.data
        try:
            with open(file_path, 'a') as file:
                file.write(data)

            with open(file_path, 'rb') as file:
                s3.upload_fileobj(file, bucket_name, file_path)

            return cs_pb2.AppendReply()  # Return an empty response

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)  # Set error code
            context.set_details("Error in appending data.")
            return cs_pb2.AppendReply()

    def DeleteFile(self, request, context):
        s3uri = request.s3uri
        try:
            object_key = file_path

            try:
                s3.head_object(Bucket=bucket_name, Key=object_key)
                s3.delete_object(Bucket=bucket_name, Key=object_key)
                response = cs_pb2.DeleteReply()
            except s3.exceptions.NoSuchKey:
                response = cs_pb2.DeleteReply()

            return response
        except Exception as e:
            response = cs_pb2.DeleteReply(  )
            return response
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    cs_pb2_grpc.add_EC2OperationsServicer_to_server(EC2OperationsServicer(), server)
    server.add_insecure_port(f"{HOST}:{PORT}")
    server.start()
    print(f"Listening on {HOST}:{PORT}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
