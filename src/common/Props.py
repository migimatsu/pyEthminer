
"""
Props.py - 共通プロパティを設定します

        ConfigParser ライブラリを利用して共通プロパティを設定します

        主処理で初期化時に一度 Props.setup() を呼び出して設定してください
        プロパティ値を利用する側では

              value     = Props.props( section, item )

        のように Props を利用してください

        エラーの場合には例外を送出します

        Props         - 共通プロパティの指定された値を返す
        SetupProps    - 共通プロパティを設定します
"""

# インポート
import      configparser            as          cp

from        typing                  import      Callable

class       Props :
    """
    共通プロパティクラス
    """
    
    # 共通プロパティ
    _props: cp.ConfigParser or None     = None
    
    # 共通プロパティの指定された値を返す
    @classmethod
    def         props( cls, section : str, item : str ) -> str :
        """
        共通プロパティの指定された値を返す

        :param section:     共通プロパティリストのセクション
        :param item:        共通プロパティリストのセクション内のアイテム
        :return:            値
        """

        # 初期化されていなければエラー
        if  not cls._props :
            raise Exception( "Props : 初期化されていません" )

        # 共通プロパティの指定された値を返す
        try :

            # 価を返す
            # noinspection PyUnresolvedReferences
            return cls._props[ section ][ item ]

        # プロパティ値がない時はエラー
        except Exception :
            raise Exception( "Props : 共通プロパティ {}.{} がありません".format( section, item ) )


    # コンストラクタ - 共通プロパティを設定する
    @classmethod
    def         setup(
            cls,
            file        : str or None           = None,
            validate    : Callable[ [], None ]  = None
        ) :
        """
        共通プロパティを設定する

        :param file:        プロパティファイル名
        :param validate:    プロファイルの各項目の値のバリデーションを行う関数
        """

        # デフォルトのプロパティファイル名
        default     = 'config.ini'

        # パーサを設定する
        if not cls._props :

            # プロパティを初期化する
            cls._props      = cp.ConfigParser()

            # プロパティファイルを読み込む - 読み込めたファイルのリストを返す
            l               = cls._props.read( file or default, encoding = 'utf-8' )

            # エラー (ファイルが読み込めない) なら例外を創出
            if not l :
                raise Exception( 'Props : プロパティファイルが読めません' )

            # プロパティの設定値を検査する
            if validate :
                validate()
