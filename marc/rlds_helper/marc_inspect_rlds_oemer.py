import tensorflow as tf

file_path = "/home/nikolaus/my_data/tensorflow_datasets/kit_irl_real_kitchen_lang2/1.0.0/kit_irl_real_kitchen_lang2-train.tfrecord-00001-of-00008"

# action_joint_state 0:7
# joint_state 0:7

# Load the TFRecord dataset
dataset = tf.data.TFRecordDataset(file_path)

# Parse and inspect the first few examples
for i, raw_record in enumerate(dataset.take(1)):  # Inspect first 3 examples
    example = tf.train.Example()
    example.ParseFromString(raw_record.numpy())
    
    print(f"\nExample {i}:")
    for key, feature in example.features.feature.items():
        # Check the type of the feature
        dtype = feature.WhichOneof('kind')
        value = getattr(feature, dtype).value
        
        # Print key, dtype, and a sample of values
        print(f"  - Key: {key}")
        print(f"    Type: {dtype}")
        if not "image" in key:
            print(f"    Values (first 5): {value[:5] if len(value) > 5 else value}")