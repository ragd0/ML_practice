# slurm概要

マークダウン記法で記載されています。マークダウンの表示できるツールで見ると多少綺麗に見えます。

---
## slurm

- slurmはジョブスケジューラであり、ジョブの投入に応じてCPU、メモリ、GPU等のリソース割当を行ったうえでジョブの実行を行います。
- ジョブにはバッチジョブとインタラクティブジョブの種類があります。

- バッチジョブ
  - `sbatch`により長時間に渡ってバックグラウンドで実行するようなバッチジョブを登録実行します。
  - バッチジョブはバックグラウンドで実行され、ジョブの出力はログファイルに記録されます。
  - 待ち時間が長い場合などはバッチジョブが向いています。
  - `sbatch`で登録するのはスクリプトであり、コマンドは登録できません。

- インタラクティブジョブ
  - `srun`でインタラクティブなジョブの実行ができます。ターミナルの接続が切れるとジョブも終了します。
  - インタラクティブジョブはコマンドの出力が画面に出力され、コマンドが終了するまで待たされます。
  - サーバとの接続が切れるとジョブも終了されます。
  - 処理時間が短い場合や、正しく実行されるか確認する場合などはインタラクティブジョブが向いています。
  - `srun`で実行できるのは単独のコマンドであり、複数コマンドは指定できません。複数コマンドを実行する場合はスクリプトにするか、`bash -c 'command1; command2'`のように1つのシェル内で複数コマンドを実行します。

- slurmのよく使うコマンド
  - sbatch: ジョブのバッチ実行(例: `sbatch スクリプトファイル名`)
  - srun: ジョブのインタラクティブ実行(例: `srun --gres=gpu:1 nvidia-smi -L`)
  - squeue: ジョブの状態確認(例: `squeue -l`)
  - scancel: ジョブの中止(例: `scancel -f ジョブID`)
  - sinfo: クラスタ状態の参照(例: `sinfo -N -l`)

- 情報源
  - [slurmの公式ページ](https://slurm.schedmd.com/)
  - [slurmコマンドマニュアル](https://slurm.schedmd.com/man_index.html)
  - [slurmチートシート](https://slurm.schedmd.com/pdfs/summary.pdf)

---
## コンテナ

- slurmでジョブを実行する際には必ずしもコンテナは必要ありません。システムにインストール済みのツールやライブラリで足りているようであればコンテナ無しでジョブを実行することもできます。
  - 例: GPUを1つ割り当ててnvidia-smi -Lコマンドを実行する。
    - $ `srun --gres=gpu:1 nvidia-smi -L`
  - 例: GPUを1つ割り当てて複数のコマンドを実行する。
    - $ `srun --gres=gpu:1 bash -c 'nvidia-smi -L; sleep 60'`

- しかし、ツールやライブラリの追加インストールが必要だったり、ライブラリのバージョンを変えたりしたい場合にはコンテナが必要になります。
- slurmはenrootコンテナとapptainerコンテナに対応しているので、いずれかのコンテナを利用します。
- dockerコンテナイメージはそのままでは使えません。インポートしてenrootコンテナイメージやとapptainerコンテナイメージに変換してから使用します。

### enroot

- enrootはNvidia推奨のコンテナ実行環境です。
- enrootのコンテナはenroot自身で作り出すこともできますし、dockerイメージをインポートして使うこともできます。
- 情報源
  - [enrootの公式ページ](https://github.com/NVIDIA/enroot)
  - [本家のマニュアル](https://github.com/NVIDIA/enroot/blob/master/doc/usage.md)

### apptainer (旧名: sigularity)

- enrootとは別のコンテナ実行環境です。
- enrootがシンプルさを売りにしているのと比較し、apptainerはdockerを完全に置き換えるフル機能を主眼に開発されているようです。
- 情報源
  - [apptainer公式ページ](https://apptainer.org/)

### pyxis (enroot+pyxis)

- enrootのコンテナをslurmから扱えるよう、slurmのコマンドオプションを拡張するプラグインがpyxisです。
- pyxisを直接使うことはなく、slurmのジョブ投入コマンド(srunなど)に対してpyxisの拡張オプションが追加されているので、それを使用します。
- slurm, pyxis, enrootの呼び出し関係: slurm -> pyxis -> enroot
- pyxisによるslurmオプションの拡張
  - [pyxisにより拡張されるオプション](https://github.com/NVIDIA/pyxis/wiki/Usage)
  - `--container-image`は使用するenrootイメージを指定するpyxisによる拡張オプションです。
  - `--container-mounts`はカレントディレクトリをコンテナのカレントディレクトリにマウントするpyxisによる拡張オプションです。これにより、カレントディレクトリ配下にあるプログラムやデータをコンテナから参照できるようにします。
  - `--container-mount-home`はホームディレクトリをコンテナにマウントするpyxisによる拡張オプションです。ホームを介してのデータのやり取りがある場合にのみ指定します。
- 情報源
  - [pyxisの公式ページ](https://github.com/NVIDIA/pyxis)

### enroot+pyxisとapptainerとの比較

- enroot+pyxis
  - メリット: pyxisがslurmに組み込まれているため手軽に使え、slurmのオプションのみでコンテナイメージ生成から実行まで完結する。
  - デメリット: コンテナイメージが~/.local/share/enroot配下に複数ファイルで置かれるため、環境の保存や復元が困難。

- apptainer
  - メリット: コンテナイメージが*.sifファイルのみで完結するため、環境の保存や復元が容易。
  - デメリット: slurmからはapptainerは一般のコマンドに見えるため、slurmのオプションとapptainerのオプションを双方考慮する必要がある。

- まとめ
  - お試しで使いたい場合や、短期的な実験等で使うならenroot+pyxisがお手軽。
  - 長期的に使う場合や、他システムにデプロイするような使い方の場合はapptainerが良い。

### docker

- dockerコンテナはdockerdを経由して起動されますが、その際にユーザの管理下から切り離されてしまい、その後の管理ができなくなります。これはslurmのようにジョブ管理を厳密に行いたいシステムでは致命的な欠点です。
- そのため、slurm上でdockerコンテナは動かせません。インポートしてenrootコンテナイメージやapptainerコンテナイメージに変換してから使用します。

- GPU計算用dockerイメージ
  - GPU計算用のdockerイメージは、[NVIDIA GPU CLOUD](https://ngc.nvidia.com/)から入手できます。enrootやapptainerのコンテナに変換して使って下さい。
  - 例えば、TensorFlowの入ったイメージは、nvcr.io#nvidia/tensorflow:24.12-tf2-py3のように指定して入手できます。
  - NVIDIA GPU CLOUDのアカウント取得は無料です。アカウント作成後、dockerでログインするためのAPI Keyを取得して下さい。

- NVIDIA GPU CLOUDへのログイン
  - NVIDIA GPU CLOUDからdockerイメージをダウンロードする際は、API Keyによるログインが必要です。
  - 毎回手動でログインを行うのは手間がかかるのと、ジョブ実行の際に都合が悪いため、`nvcrlogin`コマンドを実行し、API Keyを保存しておくと、自動ログインできるようになりま。

---
## 基本的な使い方(enroot+pyxis)

### 作業の大まかな流れ

1. enrootコンテナイメージを作成する。
2. ジョブを投入しコンテナを実行する。

### 1. enrootコンテナイメージを作成する。
- dockerイメージをベースとして、myimageという名前のenrootコンテナを作成するには以下のようにします。

- DockerHubにあるUbuntu 22.04イメージを利用する例。
  - $ `srun --container-image=ubuntu:22.04 --container-name=myimage true`

- NVIDIA GPU CLOUDのtensorflowイメージを利用する例。
  - $ `srun --container-image=nvcr.io#nvidia/tensorflow:24.12-tf2-py3 --container-name=myimage true`

- NVIDIA GPU CLOUDのpytorchイメージを利用する例。
  - $ `srun --container-image=nvcr.io#nvidia/pytorch:24.12-py3 --container-name=myimage true`

- 作成済みのコンテナに管理者権限でパッケージやpythonライブラリを追加する。
  - `--container-remap-root`オプションが必要です。
  - setup.shの中にインストール処理を書いておきます。
  - $ `chmod +x setup.sh`
  - $ `srun --container-name=myimage --container-remap-root --container-mounts=.:/workspace --container-workdir=/workspace ./setup.sh`

  - setup.shの例
```
#!/bin/bash
apt-get update		# ubuntuのパッケージデータベースをアップデート(dockerコンテナは初期状態ではデータベースが空っぽ)
apt-get install -y time	# 実行時間測定用パッケージをインストール
pip install optuna	# pythonライブラリをインストール
```

- enrootコンテナイメージの一覧表示 (コンテナイメージ名の先頭に`pyxis_`が付く)
  - $ `enroot list`

- enrootコンテナイメージの削除 (コンテナイメージ名の先頭には`pyxis_`が必要)
  - $ `enroot remove -f コンテナ名`

### 2. ジョブを投入しコンテナを実行する。

#### インタラクティブジョブの投入例

- シェルを起動し対話的にコマンドを投入(`--pty`オプションが必要)
  - $ `srun --container-name=myimage --container-mounts=.:/workspace --container-workdir=/workspace --pty bash -i`

- CPUのみを使用し、コンテナ内のコマンドを実行する。
  - $ `srun --container-name=myimage --container-mounts=.:/workspace --container-workdir=/workspace ls /home`

- コンテナ内のコマンドを実行する例(GPUを1個割り当てて、コンテナ内のコマンドnvidia-smiによりGPUの状態を表示)
  - $ `srun --gres=gpu:1 --container-name=myimage --container-mounts=.:/workspace --container-workdir=/workspace nvidia-smi`

- シェルスクリプトを起動する例(GPUを1個割り当てて何かする)
  - $ `chmod +x do_something.sh`
  - $ `srun --gres=gpu:1 --container-name=myimage --container-mounts=.:/workspace --container-workdir=/workspace ./do_something.sh`


#### バッチジョブの投入例

- バッチジョブとしてenrootコンテナを起動し処理を実行する例(GPUを1個割り当てて何かする)。
  - 処理はバックグラウンドで行われるため、ログファイル名を指定する。
  - バッチジョブはスクリプトしか指定できないので、あらかじめ用意する。
  - sbatchに渡すオプションはスクリプト上方の`#SBATCHの行に書ける。
  - $ `chmod +x pyxis_exec.sh
  - $ `sbatch pyxis_exec.sh`

  - pyxis_exec.shの例
```
#!/bin/bash
#SBATCH --gres=gpu:1 --container-name=myimage --container-mounts=.:/workspace --container-workdir=/workspace -o sbatch.log -e sbatch.log

python3 gpu_check.py
```

---
## 基本的な使い方(apptainer版)

### 作業の大まかな流れ

1. apptainerコンテナイメージファイルを作成する。
2. ジョブを投入しコンテナを実行する。

### 1. apptainerコンテナイメージファイルを作成する。

- 参照: <https://gitlab.com/tetsuyasu/apptainer_example>

### 2. ジョブを投入しコンテナを実行する。

#### インタラクティブジョブの投入例(イメージapptainer/image.sifを使用)

- シェルを起動し対話的にコマンドを投入(`--pty`オプションが必要)
  - $ `srun --pty apptainer exec --bind ${PWD}:${PWD} --nv apptainer/image.sif bash`

- CPUのみを使用し、コンテナ内のコマンドを実行する。
  - $ `srun apptainer exec --bind ${PWD}:${PWD} --nv apptainer/image.sif ls /home`

- コンテナ内のコマンドを実行する例(GPUを1個割り当てて、コンテナ内のコマンドnvidia-smiによりGPUの状態を表示)
  - $ `srun --gres=gpu:1 apptainer exec --bind ${PWD}:${PWD} --nv apptainer/image.sif nvidia-smi`

- シェルスクリプトを起動する例(GPUを1個割り当てて何かする)
  - $ `chmod +x do_something.sh`
  - $ `srun --gres=gpu:1 apptainer exec --bind ${PWD}:${PWD} --nv apptainer/image.sif ./do_something.sh`

#### バッチジョブの投入例

- イメージapptainer/image.sifを使ってコンテナを起動し処理を実行する例(GPUを1個割り当てて何かする)。
  - 処理はバックグラウンドで行われるため、ログファイル名を指定する。
  - バッチジョブはスクリプトしか指定できないので、あらかじめ用意する。
  - sbatchに渡すオプションはスクリプト情報の`#SBATCHの行に書ける。
  - $ `chmod +x apptainer_exec.sh`
  - $ `sbatch apptainer_exec.sh`

  - apptainer_exec.shの例
```
#!/bin/bash
#SBATCH --gres=gpu:1 -o sbatch.log -e sbatch.log

apptainer exec --bind ${PWD}:${PWD} --nv apptainer/image.sif nvidia-smi
```

---
