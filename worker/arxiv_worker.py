import urllib.request
import os
import tarfile
import tempfile
import pypandoc

def fetch_and_convert_tex(id):
    with tempfile.TemporaryDirectory() as workdir:
        # download an archive from arXiv
        archive_path = os.path.join(workdir, 'archive.tar.gz')
        urllib.request.urlretrieve("https://arxiv.org/e-print/{}".format(id), archive_path)

        # extract the archive
        tar = tarfile.open(archive_path)
        tar.extractall(workdir)
        tar.close()

        # DEBUG
        print('List of contents', os.listdir(workdir))

        # search for a TeX source
        tex_files = [x for x in os.listdir(workdir) if x.endswith('.tex')]
        print('TeX', tex_files)
        if len(tex_files) == 0:
            return False
        tex_filepath = os.path.join(workdir, tex_files[0])
        print(tex_filepath)

        # convert a TeX source to HTML
        pandoc_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../pandoc')
        os.chdir(workdir)
        extra_args = [
            '--self-contained',
            '--data-dir', pandoc_dir
        ]

        print(pandoc_dir)
        print(os.listdir(pandoc_dir))

        output = pypandoc.convert_file(tex_filepath, 'html5', extra_args=extra_args)

        return output
