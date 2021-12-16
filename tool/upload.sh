#!/bin/bash

# This script can be used during development to upload the firmware to the pi
# that runs the Smart Pot Hub. You still have to connect to the pi via SSH to
# restart the service.

# Upload all files in the current directory.
input_dir="."

# Before the files are uploaded, they are written to a `.tar` archive and
# compressed with Gzip to a `.tar.gz` file.
tar_file="smart-pot-hub.tar"
tar_gz_file="$tar_file.gz"

# The host and user name were to upload the archive to.
ssh_user="pi"
ssh_host="smart-pot-hub"

# Paths on the pi where to upload the archive and where to extract it.
upload_path="/home/$ssh_user"
extract_path="$upload_path/smart-pot-hub"

# Stop script on first error.
set -e

# Create source code archive.
echo "Creating archive..."
git ls-files "$input_dir" -z | xargs -0 tar rvf "$tar_file"

# Compress source code archive.
echo "Compressing archive..."
gzip -c "$tar_file" > "$tar_gz_file"

# Copy the archive to the pi.
echo "Uploading archive..."
scp "$tar_gz_file" "$ssh_user@$ssh_host:$upload_path" 2>&1

# Extract the archive.
echo "Extracting archive..."
ssh "$ssh_user@$ssh_host" """\
mkdir -p '$extract_path'
cd '$extract_path'
tar xvf '$upload_path/$tar_gz_file'
rm '$upload_path/$tar_gz_file'
"""

# Clean up.
echo "Removing archive..."
rm "$tar_file"
rm "$tar_gz_file"
