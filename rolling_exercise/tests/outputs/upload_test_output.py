from starlette import status


test_valid_data_output = status.HTTP_201_CREATED

test_invalid_dates_output = status.HTTP_400_BAD_REQUEST

test_missing_data_output = status.HTTP_400_BAD_REQUEST
