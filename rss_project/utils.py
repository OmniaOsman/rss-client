from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response


class ResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


def process_request(input_serializer_class, output_serializer_class, action_function, request, use_query_params=False,mixed_data=False):
    # Determine the source of input data (query params or body)
    input_data = request.query_params if use_query_params else request.data

    if mixed_data:
        input_data= request.data
        input_data.update(request.query_params.dict())

    if input_serializer_class:
        # Deserialize and validate input data
        input_serializer = input_serializer_class(data=input_data, context={'request': request})
        input_serializer.is_valid(raise_exception=True)
    
        # Perform the action using validated data
        action_response = action_function(input_serializer.validated_data, request)

        # Serialize the action response data
        output_serializer = output_serializer_class(data=action_response)
        output_serializer.is_valid(raise_exception=True)
    else:
        output_serializer = output_serializer_class(data=action_function(request, request))
        output_serializer.is_valid(raise_exception=True)
        
    return Response(output_serializer.data, status=status.HTTP_200_OK)


def process_query_params(query_params):
    data = {}
    for key, value in query_params.items():
        if key.endswith("[]"):
            data[key[:-2]] = query_params.getlist(key)
        else:
            data[key] = value
    return data
    