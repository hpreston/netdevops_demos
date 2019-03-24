#! /usr/bin/env python

from os import listdir, system, makedirs
from os.path import isdir, isfile, join, exists
from shutil import rmtree
from jinja2 import Template

recordings_dir = "../recordings"  # Source or Genie recordings
mocks_dir = "../mocks"  # Destination for all mock devices
testbed_dir = "../testbeds"

# Open and create Testbed Temlate
testbed_template_file = "template.j2"
with open(testbed_template_file) as f:
    testbed_template = Template(f.read())

# Command template to create Unicon mocks
create_mock = "python -m unicon.playback.mock --recorded-data {recorded_data} --output {output}"

# Get a list of all recordings created
recordings  = listdir(recordings_dir)

# Process each recording and all devices contained
for recording in recordings:
    # Make sure recording is a directory
    if not isdir(join(recordings_dir, recording)):
        print("{} is not a directory.".format(recording))
        continue

    # Create full path variables
    recording_path = join(recordings_dir, recording)
    output_dir = join(mocks_dir, recording)

    print("Processing Recording {}".format(recording_path))

    # Cleanup from previous mock creations
    if exists(output_dir):
        print("Mock Output Directory {} exists, deleting it and all contents.".format(output_dir))
        rmtree(output_dir)


    # Get list of devices from recording
    device_recordings = [ f for f in listdir(recording_path) if isfile(join(recording_path, f)) ]

    # Process each device recording and create a device mock
    for device_recording in device_recordings:
        # path to recorded data for this device
        recorded_data = join(recording_path, device_recording)

        # Create directory for the mocks for this recording
        device_mock_output_dir = join(output_dir, device_recording)
        makedirs(device_mock_output_dir)


        # path for the Mock output file
        output = "{}.yaml".format(join(device_mock_output_dir, device_recording))

        # Create command to create the mock
        command = create_mock.format(recorded_data = recorded_data, output = output)

        # Execute the create mock command
        # ToDo: just import the unicon mock library and run in code
        exec = system(command)

        # Verify successful creation
        if exec != 0:
            print("Problem creating mock for {}".format(recorded_data))

    # Create Testbed file
    testbed = testbed_template.render(devices = device_recordings, name = recording)
    with open(join(testbed_dir, "mock_{}_tb.yaml".format(recording)), "w") as f:
        f.write(testbed)

    print("")
