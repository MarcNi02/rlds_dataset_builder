import tensorflow as tf
from pathlib import Path

base_dir = Path("/home/nikolaus/my_data/flower_datasets/kit_irl_real_kitchen_lang_marc_new_kitchen/1.0.0")

out_dir = base_dir / "test_first_images"
out_dir.mkdir(parents=True, exist_ok=True)

id = 0

# instructions = []

# Loop through all 16 tfrecord files
for file_idx in range(4):
    file_path = base_dir / f"kit_irl_real_kitchen_lang_marc_new_kitchen-train.tfrecord-000{file_idx:02d}-of-00004"
    dataset = tf.data.TFRecordDataset(str(file_path))
    
    print(f"Scanning file: {file_path}")
    
    for raw_record in dataset:
        example = tf.train.Example()
        example.ParseFromString(raw_record.numpy())

        for key, feature in example.features.feature.items():
            # print(key)
            if "language_instr" in key:
                dtype = feature.WhichOneof('kind')
                value = getattr(feature, dtype).value
                instruction = value[0].decode("utf-8")
                
                # if "pot" in instruction and "sink" in instruction and "right" in instruction and "stove" in instruction:-
                # if "banana" in instruction and "sink" in instruction and "right" in instruction and "stove" in instruction:
                # if instruction == 'Move the banana from the right stove to the sink.':
                if "ut the banana from the sink to the right stove." in instruction:
                    print(f"Matched: {instruction}")
                    # instructions.append(instruction)
                    
                    sample_out_dir = out_dir / f"{id}.jpeg"
                    
                    # Save image_top
                    value = getattr(example.features.feature["steps/observation/image_top"], 
                                    example.features.feature["steps/observation/image_top"].WhichOneof('kind')).value
                    with open(sample_out_dir, "wb") as f:
                        f.write(value[0])

                    id += 1

# print(f"set instructions {set(instructions)}")
# set instructions {
# 'Move the banana from the right stove to the sink.', 'Transfer the banana from the sink to the right stove.', 
# 'Transfer the banana from the right stove to the sink.', 'Take the banana from the sink and place it onto the right stove.', 
# 'Take the banana from the stove on the right and put it in the sink.', 'Move the banana from the sink to the right stove.'}