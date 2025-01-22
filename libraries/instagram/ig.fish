#!/usr/bin/env fish
# Dependencies: fish, kubectl, libraries k8s project, curl, gunzip, jq (optional)
set DEFAULT_USERNAME ccalibraries
set file instagram.json
set username $DEFAULT_USERNAME

if contains help $argv || contains -- -h $argv || contains -- --help $argv
    echo -e "\tUsage: ./libraries/instagram/ig.fish [username]\n"
    echo "Update the Instagram post on the home page. Uses the $DEFAULT_USERNAME account by default. This script downloads JSON data from Instagram, pushes to a running pod based on the NS env var, and runs the instagram management command that creates a new Instagram object and downloads its media."
end

if not set --query NS
    set_color red
    echo "Error: requires an NS namespace env var corresponding to one of the libraries' kubernetes environments: libraries-wagtail (local), lib-ep (staging), lib-production. See our k8s project for more information on NS and our namespaces: https://github.com/cca/libraries-k8s" >&2
    set_color normal
    exit 1
end

if [ (count $argv) -gt 0 ]
    set username $argv[1]
end

# app id should not change often
# may need to update User Agent periodically?
set response_code (curl --output $file.gz --write-out "%{response_code}" \
    --header "x-ig-app-id: 936619743392459" \
    --header "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36" \
    --header "Accept-Language: en-US,en;q=0.9,ru;q=0.8" \
    --header "Accept-Encoding: gzip, deflate, br" \
    --header "Accept */*" \
    "https://i.instagram.com/api/v1/users/web_profile_info/?username=$username")

if [ $response_code -ne 200 ]
    gunzip $file.gz
    echo "HTTP $response_code Error"
    if command --query jq
        echo "Instagram response:"
        jq $file
    else
        echo "See response data in $file"
    end
    exit 1
end

# unzip, copy to app pod, and pass to mgmt cmd
gunzip $file.gz
and k cp $file (k8 pod):/tmp/$file
and k exec (k8 pod) -- python manage.py instagram --json /tmp/$file
if [ $status -eq 0 ]
    rm -v $file
end
