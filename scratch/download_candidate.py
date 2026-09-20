import os
import urllib.request

os.makedirs('scratch/candidates', exist_ok=True)

def download(pid_or_url, name):
    if pid_or_url.startswith('http'):
        url = pid_or_url
        if '?' not in url:
            url += '?auto=format&fit=crop&w=1200&h=800&q=80'
    else:
        pid = pid_or_url
        if not pid.startswith('photo-'):
            pid = 'photo-' + pid
        url = f'https://images.unsplash.com/{pid}?auto=format&fit=crop&w=1200&h=800&q=80'
    
    out_path = os.path.join('scratch/candidates', name + '.jpg')
    print(f'Downloading {url} to {out_path}...')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(out_path, 'wb') as f:
                f.write(data)
        print(f'SUCCESS: {out_path} ({len(data)} bytes)')
        return out_path
    except Exception as e:
        print(f'FAILED: {e}')
        return None

if __name__ == '__main__':
    download('1571878385238-2d89b27962b1', 'mag_1571878385238')
    download('1547057740-4b18aac8eed2', 'mag_1547057740')
