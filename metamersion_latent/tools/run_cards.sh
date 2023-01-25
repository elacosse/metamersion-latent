

print_usage() {
  printf "Usage: run_cards.sh <input_directory_path> <configuration_filepath> <output_directory> -p (optional) -c (optional)"
}

# create output directory if doesn't exist
if [ ! -d $3 ]; then
    mkdir $3
fi

p_flag=false
c_flag=false
for arg in "$@"
do
  if [ "$arg" == "-p" ]; then
    p_flag=true;
    echo "Running in parallel"
  elif [ "$arg" == "-c" ]; then
    c_flag=true;
  elif [ "$arg" == "-h" ]; then
    print_usage
    exit 0
  fi
done

# Run CHATS on all the files in the directory
if [ $p_flag == false ]; then
    for file in $1/*.yaml; do
        echo "Processing $file"
        if [ $c_flag == true ]; then
            python metamersion_latent/tools/run_card.py -c $2 -e $file -o $3 -p
        else
            python metamersion_latent/tools/run_card.py -c $2 -e $file -o $3
        fi
    done
    exit 0
fi
if [ $p_flag == true ]; then
    echo "Running in parallel"
    for file in $1/*.yaml; do
        echo "Processing $file"
        if [ $c_flag == true ]; then
            python metamersion_latent/tools/run_card.py -c $2 -e $file -o $3 -p &
        else
            python metamersion_latent/tools/run_card.py -c $2 -e $file -o $3 &
        fi
    done
fi


