#!/bin/bash
avg_time() {
    #
    # usage: avg_time n command ...
    #
    n=$1; shift
    (($# > 0)) || return                   # bail if no command given
    for ((i = 0; i < n; i++)); do
        { time -p "$@" &>/dev/null; } 2>&1 # ignore the output of the command
                                           # but collect time's output in stdout
    done | awk '
        /user/ { user = user + $2; nu++ }
        END    {
                 if (nu>0) printf("user %f\n", user/nu);
               }'
}

# echo "test-1.txt brute force"
# avg_time 100 python main.py tests/test-1.txt
# echo "test-1.txt plane sweep"
# avg_time 100 python main.py tests/test-1.txt --plane-sweep
# echo "test-2.txt brute force"
# avg_time 100 python main.py tests/test-2.txt
# echo "test-2.txt plane sweep"
# avg_time 100 python main.py tests/test-2.txt --plane-sweep
# echo "test-3.txt brute force"
# avg_time 100 python main.py tests/test-3.txt
# echo "test-3.txt plane sweep"
# avg_time 100 python main.py tests/test-3.txt --plane-sweep
echo "test-4.txt brute force"
avg_time 100 python main.py tests/test-4.txt
echo "test-4.txt plane sweep"
avg_time 100 python main.py tests/test-4.txt --plane-sweep
# echo "test-5.txt brute force"
# avg_time 100 python main.py tests/test-5.txt
# echo "test-5.txt plane sweep"
# avg_time 100 python main.py tests/test-5.txt --plane-sweep
