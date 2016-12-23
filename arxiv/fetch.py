import urllib.request
import sys
import os
from os.path import join
import shutil
import tarfile
import tempfile
import pypandoc

# https://arxiv.org/abs/1609.01704v5 or 1609.01704v5
# to
# https://arxiv.org/e-print/1609.01704v5

def extract_html(id):
    with tempfile.TemporaryDirectory() as workdir:
        archive_path = join(workdir, 'archive.tar.gz')
        download(id, archive_path)
        tar = tarfile.open(archive_path)
        tar.extractall(workdir)
        tar.close()

        tex_files = [x for x in os.listdir(workdir) if x.endswith('.tex')]
        print(tex_files)
        if len(tex_files) == 0:
            return False

        tex_filepath = join(workdir, tex_files[0])
        print(tex_filepath)

        templates_dir = join(os.path.dirname(os.path.realpath(__file__)), '../pandoc/templates')
        shutil.copytree(templates_dir, join(workdir, 'templates'))

        output = pypandoc.convert_file(tex_filepath, 'html5', extra_args=['--self-contained', '--data-dir', workdir])
        return output

if __name__ == '__main__':
    data = extract_html('1612.04811v1')
    print(data)
