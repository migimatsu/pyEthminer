"""
Args.py - コマンド引数を設定します

        argparse ライブラリを利用してコマンド引数を解析し設定します

        主処理で初期化時に一度 SetupArgs() を呼び出して設定してください
        コマンド引数を得る側では

              value     = Args( key )

        のように Args を利用してください

        エラーの場合には例外を送出します

        Args          - コマンド引数の指定された値を返す
        SetupArgs     - コマンド引数を設定します
"""

# インポート
import          sys
import          argparse        as      ap
from            typing          import  Callable, Dict, List

# コマンド引数
_args : Dict[ str, str ] or None        = None

# コマンド引数の指定された値を返す
def         Args( key : str ) -> str :
    """
    コマンド引数の指定された値を返す

    :param key:         コマンド引数の引数名
    :return:            値
    """

    # 初期化されていなければエラー
    if not _args :
        raise Exception( "Args : 初期化されていません" )

    # コマンド引数に指定された値を返す
    try :

        # 価を返す
        # noinspection PyUnresolvedReferences
        return _args[ key ]

    # プロパティ値がない時はエラー
    except Exception :
        raise Exception( "Args : コマンド引数にオプション {} がありません".format( key ) )

# コマンド引数を設定する
def         SetupArgs(
                spec        : List[ Dict[ str, str or Dict[ str, str ] ] ] = None,
                validate    : Callable[ [], None ]  or None = None,
            ) -> None :
    """
    コマンド引数を設定する

    コマンド引数定義 spec は、 以下の形式のリストで渡すこと
                [   {   name : <位置引数名、または、オプション引数名>         # 必須
                        [, long : <ロングオプション引数名> ]                 # オプション引数は必須
                        [, kwargs : { <key> = <value>, ... } ]              # argparse.add_argument の kwargs そのまま
                    },
                    ...
                ]
    :param spec:        コマンド引数定義
    :param validate:    プロファイルの各項目の値のバリデーションを行う関数
    :return:            None. エラーの時は例外オブジェクトを返す
    """

    global _args

    # 引数パーサを得る
    _parser         = ap.ArgumentParser( description = 'RA のダミー ME サービスを登録する CSV を生成します',
                                         exit_on_error = False )

    # すべてのコマンド引数定義を設定する
    for s in spec if spec else [] :

        # 引数定義をパーサに設定する
        _parser.add_argument( s[ 'name' ], s[ 'long' ], ** s[ 'kwargs' ] )

    # コマンド引数を解析する
    try :

        # パーサを呼び出し、結果を辞書に変換して格納する
        _args             = vars( _parser.parse_args() )

        # 生のコマンド引数を $0, $2, ... として格納する
        argc            = 0

        for arg in sys.argv :
            _args[ '${:d}'.format( argc ) ]         =  arg
            argc                                    += 1

    # 引数エラーのときは例外を返す
    except :
        raise Exception( 'Args : コマンド引数のエラーです' )

    # 引数の内容の検査を行う
    if validate :
        validate()

    # 正常終了 - None を返す
    return None
