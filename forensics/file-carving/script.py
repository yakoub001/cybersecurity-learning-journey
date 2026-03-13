# simple_file_carver.py

input_file = "input.bin"
output_file = "carved_image.jpg"

# JPEG signatures
jpeg_header = b'\xff\xd8\xff'
jpeg_footer = b'\xff\xd9'

with open(input_file, "rb") as f:
    data = f.read()

start = data.find(jpeg_header)
end = data.find(jpeg_footer)

if start != -1 and end != -1:
    end += 2  # include footer bytes

    carved_data = data[start:end]

    with open(output_file, "wb") as img:
        img.write(carved_data)

    print("Image carved successfully!")
else:
    print("JPEG image not found.")
