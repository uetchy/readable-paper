import urllib.request
import sys
import os
from os.path import join
import tarfile
import tempfile
import pypandoc

def fetch_and_convert_tex(id):
    with tempfile.TemporaryDirectory() as workdir:
        # download an archive from arXiv
        archive_path = join(workdir, 'archive.tar.gz')
        urllib.request.urlretrieve("https://arxiv.org/e-print/{}".format(id), archive_path)

        # extract the archive
        tar = tarfile.open(archive_path)
        tar.extractall(workdir)
        tar.close()

        # search for a TeX source
        tex_files = [x for x in os.listdir(workdir) if x.endswith('.tex')]
        print(tex_files)
        if len(tex_files) == 0:
            return False
        tex_filepath = join(workdir, tex_files[0])
        print(tex_filepath)

        # convert a TeX source to HTML
        os.chdir(workdir)
        pandoc_dir = join(os.path.dirname(os.path.realpath(__file__)), './pandoc')
        print('pandocdir', pandoc_dir)
        output = pypandoc.convert_file(tex_filepath, 'html5', extra_args=['--self-contained', '--data-dir', pandoc_dir])

        return output