import os
import piexif
import datetime
import argparse
import shutil
import filecmp


def to_path(imageFile):
    """
    exif情報からコピー先のPATHを作成する
    """
    i = piexif.load(imageFile)
    e = os.path.splitext(imageFile)
    d = i['Exif'][piexif.ExifIFD.DateTimeOriginal]

    tdatetime = datetime.datetime.strptime(d.decode('utf-8'), '%Y:%m:%d %H:%M:%S')
    directory_name = datetime.datetime.strftime(tdatetime, '%Y/%Y-%m/')
    file_name = datetime.datetime.strftime(tdatetime, '%Y%m%d_%H%M%S')

    return os.path.join(directory_name, file_name + e[1])


def add_serial(path, count=1):
    """
    添字をつけるが、ファイルが存在する場合はカウントアップする
    """

    dir, file = os.path.split(path)
    name, ext = os.path.splitext(path)
    new_path = os.path.join(dir, name + '_' + str(count) + ext)

    print(f'新しいPATH{new_path}')

    if os.path.isfile(new_path) == True:
        add_serial(path, count + 1)
    else:
        return new_path


def action(from_path, to_path):
    """
    指定されたファイルをディレクトリにコピーする
    """

    # 既にそのファイルが存在し、を比較して違うファイルの場合は連番をつける
    if os.path.isfile(to_path) == True and filecmp.cmp(from_path, to_path) == False:
        print('同じファイル名のものがあったのでリネームします')
        to_path = add_serial(to_path)
    elif os.path.isfile(to_path) == True and filecmp.cmp(from_path, to_path) == True:
        print(f'既にファイルが存在しているのでコピーしませんでした{from_path} =====>> {to_path}')
        return

    print(f'copy {from_path} =====>> {to_path}')
    
    # コピー先のディレクトリを作成する
    dir, file = os.path.split(to_path)
    os.makedirs(dir, exist_ok=True)
    shutil.copy2(from_path, to_path)

    return


if __name__ == '__main__':

    # 引数の処理
    parser = argparse.ArgumentParser(description='指定したディレクトリ内にある画像ファイルからEXIF情報を解析し指定したディレクトリへ年月を指定したディレクトリを作成した後コピーします。')

    parser.add_argument('fromPath', help='コピー元のディレクトリ') 
    parser.add_argument('toPath', help='コピー先のディレクトリ') 

    args = parser.parse_args() 

    for root, dirs, files in os.walk(top=args.fromPath):
        for file in files:
            # コピー元ファイル
            _from = os.path.join(root, file)
            # コピー先ファイル
            try:
                _to = to_path(_from)
            except piexif.InvalidImageDataError:
                print(f'Exif情報が取得できなかったのでスキップします file:{_from}')
                continue
            except:
                print('なにかおかしいので停止します')
                exit(1)

            action(_from, os.path.join(args.toPath, _to))


