import urllib.request
import os
import tarfile
import tempfile
import pypandoc
import pymongo

# setup database
mongodb_url = os.environ.get('MONGODB_URI', 'mongodb://mongo:27017/db')
mongo_client = pymongo.MongoClient(mongodb_url)
db = mongo_client.get_default_database()


def fetch_and_convert_tex(id):
    try:
        with tempfile.TemporaryDirectory() as workdir:
            print('PATH', os.environ['PATH'])

            # download an archive from arXiv
            archive_path = os.path.join(workdir, 'archive.tar.gz')
            urllib.request.urlretrieve(
                "https://arxiv.org/e-print/{}".format(id), archive_path)

            # extract the archive
            tar = tarfile.open(archive_path)
            tar.extractall(workdir)
            tar.close()

            # DEBUG
            print('List of contents', os.listdir(workdir))

            # search for a TeX source
            tex_files = [x for x in os.listdir(workdir) if x.endswith('.tex')]
            print('TeX', tex_files)

            def hasDC(texpath):
                with open(os.path.join(workdir, texpath), 'r') as f:
                    if "documentclass" in f.read():
                        return True
                    else:
                        return False

            tex_files = list(filter(hasDC, tex_files))

            if len(tex_files) == 0:
                return False

            tex_filepath = os.path.join(workdir, tex_files[0])
            print(tex_filepath)

            # convert a TeX source to HTML
            pandoc_dir = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), '../pandoc')
            os.chdir(workdir)
            extra_args = ['--self-contained', '--data-dir', pandoc_dir]

            print(pandoc_dir)
            print(os.listdir(pandoc_dir))

            output = pypandoc.convert_file(
                tex_filepath, 'html5', extra_args=extra_args)

            paper_id = db.papers.insert_one({
                "arxiv_id": id,
                "content": output
            }).inserted_id

            return paper_id
    except Exception:
        pass
