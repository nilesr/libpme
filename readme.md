# PNG Metadata Editor

This library was written for a competition between me and Ethan, who was going to write this same thing in Java. He failed.

You can initialize a PME instance by passing it a filename to an already existing file, or no arguments, like this:

    img = new libpme.PME("test.png");
	# or
    img = new libpme.PME();

If the file is not valid, it will throw an exception

## Properties

These are the values that you can access or change. Most are self explanatory. Changing any of these will automatically call `recalculate_IHDR`. If you really want to suppress this behavior, just back up the IHDR chunk before changing the value. The defaults for an object created with no filename are displayed in parenthesis

	width (0)
	height (0)
	bit_depth (8)
	color_type (color_types.RGB_WITH_ALPHA (6))
	compression_method (0)
	filter_method (0)
	interlace_method (0)

## Methods
Here are the methods you can call on an image, in no particular order

### `recalculate_properties`
This simply recalculates the seven properties listed above from the data currently in the IHDR chunk. 

	img.height = 400
	img.chunks[0][2] = b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\x06\x00\x00\x00'
	# img.height remains unchanged at 400
	img.recalculate_properties()
	# img.height is now set to 0

### `recalculate_IHDR`
This takes the seven properties listed above and destructively replaces the first chunk's data and crc with updated fields

	img.width = 0
	# img.chunks[0][2] is now set to b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\x06\x00\x00\x00'
	img.width = 400
	img.recalculate_IHDR()
	# img.chunks[0][2] is now set to b'\x00\x00\x01\x90\x00\x00\x00\x00\x08\x06\x00\x00\x00'

### `recalculate_crc`
This takes an index of a chunk (see below) and overwrites the crc in that chunk with a newly calculated crc based on that chunk's label and data

	img.color_type = libpme.color_types.RGB
	img.width = img.height = 1
	img.chunks[1][2] = b'\x00\xFF\x00\x00' # a 1x1 red image, assuming that the second chunk is the only IDAT chunk
	img.recalculate_crc(1) # img.chunks[1][3] is now set to b'T\xbb\xd3\xea'

### `recalculate_length`
This takes an index of a chunk (see below) and updates the length of that chunk with a newly calculated length based on that chunk's data

	img.color_type = libpme.color_types.RGB
	img.width = img.height = 1
	img.chunks[1][2] = img.compress(b'\x00\xFF\x00\x00') # a 1x1 red image, assuming that the second chunk is the only IDAT chunk
	img.recalculate_length(1) # img.chunks[1][0] is now set to b'\x00\x00\x00\x04'

### `save`
This saves the image to the disk, overwriting a file if it was already there. If the object was created from an existing file and no arguments are passed, it will use the original file. 

	img.save("red1.png")
	img.save() # Only if the object was created from an existing file.

### `get_concatenated_idat_data`
Concatenates the (still compressed) data of each IDAT chunk, then returns it.

	img.width = 2
	img.chunks.insert(2, [b'\x00\x00\x00\x03', b'IDAT', img.compress(b'\x00\xFF\x00'), b'j\xee\xb3\xd0']) # making it a 2x1 image with a red and a green pixel
	img.decompress(img.get_concatenated_idat_data()) # returns '\x00\xFF\x00\x00\x00\xFF\x00';

### `write_raw_idat_data`
Deletes all IDAT chunks except the first one, then sets that chunk's data to the argument it was passed, and recalculates its crc and length.

	img.write_raw_idat_data(img.compress(b'\x00\x00\x00\xFF\x00\x00\xFF')) # a 2x1 image with all blue pixels

## Indexes
Any function that takes an index can be passed either the numerical index of the chunk (so 0 for IDAT, 1 for the second chunk, -1 for the last chunk, etc..), or a list that exists in `img.chunks`, or a 4-length bytes object that is equal to the label of one of the chunks in the image. If a chunk with that label appears more than once, the first one will be used

## Color types
The following color types are defined

    GREYSCALE = 0
    RGB = 2
    PALETTE = 3
    GREYSCALE_WITH_ALPHA = 4
    RGB_WITH_ALPHA = 6
