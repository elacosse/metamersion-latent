# Usage: run_chats.sh <input_directory_path> <configuration_filepath> <output_directory>

# Check for the correct number of arguments
if [ $# -ne 3 ]; then
    echo "Usage: run_chats.sh <input_directory_path> <configuration_filepath> <output_directory>"
    exit 1
fi

# Run CHATS on all the files in the directory
for file in $1/*.py; do
    echo "Processing $file"
    python metamersion_latent/tools/run_chat.py -c $2 -e $file -o $3
done

