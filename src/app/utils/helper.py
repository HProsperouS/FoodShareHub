import base64
import six
import io


def decode_base64_file(data):
    """
    Fuction to convert base 64 to readable IO bytes a
    :param data: base64 file input
    :return: tuple containing IO bytes file 
    """
    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            TypeError('invalid_image')

        return io.BytesIO(decoded_file)


