"""
Log.py - 共通ロガーの設定をします

        logging ライブラリを利用してロギング環境を設定します

        主処理で初期化時に一度 SetupLogger() を呼び出して設定してください
        ロガーを使うモジュールでは

              log     = Log( __name__ )

        のように宣言してロガーを利用してください

        logger        - ロガーを得る
        SetupLogger   - ロがーを初期化します
        LogFilter     - ログの抑止フィルタクラス
"""

# インポート
import      sys
import      os
from        re              import      compile, Pattern
import      logging
from        logging         import      Logger, getLogger
from        logging         import      basicConfig, LogRecord, StreamHandler, Filter
from        typing          import      List

# 初期化フラグ
_Logger  : bool         = False

# 出力するログのレベル - logging クラスのレベル名または int (0 ですべて) で指定してください
DEBUG    : int          = logging.DEBUG
INFO     : int          = logging.INFO
WARNING  : int          = logging.WARNING
ERROR    : int          = logging.ERROR
FATAL    : int          = logging.FATAL
CRITICAL : int          = logging.CRITICAL

# ロガーを返す
def         Log( name : str ) -> Logger :
    """
    ロガーを返す
    各ファイルはこのメソッドでロガーを作成してください
    
    :param name:    ロガー名（通常はそのファイルの __name__)
    :return:        ロガー
    """

    global _Logger

    # 初期化されていなければエラー
    if not _Logger :
        raise Exception( "Log : 初期化されていません" )

    # 指定した名前のロガーを返す
    return getLogger( name )

# 異常終了時のロガー
def         abort( msg : str, e : Exception = "", trace : bool = True ) -> None :
    """
    異常終了時のロガー

    メッセージとトレースを出力して終了します

    :param msg:     メッセージ
    :param e:       原因となった例外
    :param trace:   トレースが不要な場合に False とする
    :return:        なし
    """

    # ロガー
    log         = Log( __name__ )

    # メッセージを出力する
    log.fatal( "!!! {0} ( {1} )".format( msg, e ), exc_info = trace )

    # 異常終了する
    log.fatal( "!!! 終了します" )

    exit( -1 )

# ルートロガーの設定を行うクラス
class       SetupLog :
    """
    ルートロガーの設定を行うクラス

    ルートロガーの基本設定を行うことにより、各ファイルでの logger はこれを引き継ぐ
    """

    # 特定の名前のロガーのログを抑止するフィルタクラス
    class       Filter( Filter ) :
        """
        特定の名前のロガーのログは抑止する
        """

        # 出したくないログのロガー名称（正規表現）
        deter : List[ Pattern ]      = [

            compile( "^matplotlib.*$" ),                    # matplotlib パッケージからのログ
            # 必要あればここに追加して下さい
        ]

        # ロガー名でのフィルタリングを行う
        def filter( self, rec: LogRecord ) -> bool :
            """
            利用するライブラリから不要な INFO, DEBUG ロギングがされることがあるため、ロガー名でのフィルタリングを行う

            :param rec:         ログレコード
            :return:            ログを True なら出力、False なら抑止する
            """

            # ロガー名がマッチしたら False を返す（抑止する）
            for d in self.deter :

                # 名前が正規表現に合致したら抑止する
                if d.match( rec.name ) :
                    return False

            # そうでなければ True を返す（そのまま出力する）
            return True

    # ログフォーマットを設定する
    _fmt        = '%(asctime)s [{}] %(levelname)s : %(message)s ( %(name)s:%(lineno)s )' \
        .format( os.path.basename( sys.argv[ 0 ] ) )

    # コンストラクタ
    def         __init__( self, level : int = None, fmt : str = None ) -> None :
        """
        コンストラクタ

        ルートロガーの設定を行う。WARNING 以上は無条件で stderr へ、それ以下は stdout に
        ログを出力する。ただし、フィルタで指定したロガーの出力は抑止する。

        :param level:       ログレベル。指定がなければすべて
        :param fmt:         ログフォーマット。指定がなければビルトインのフォーマット
        """

        global _Logger

        # h1 : WARNING 未満の時のハンドラ - ログを stdout に出すハンドラ
        h1          = StreamHandler( stream = sys.stdout )          # stdout へのハンドラ

        # - WARNING 未満しか出さないフィルタを設定する
        h1.addFilter( lambda r : r.levelno < WARNING )              # - WARNING 以下のみ

        # - 不要な（特定の名前のロガーからの）ログを出力しないフィルタを設定する
        h1.addFilter( self.Filter() )                               # - フィルタ内部クラス

        # h2 : WARNING 以上の時のハンドラ - ログを stderr に出すハンドラ
        h2          = StreamHandler( stream = sys.stderr )          # stderr へのハンドラ

        # - WARNING 以上のみ出す
        h2.setLevel( WARNING )                                      # - WARNING 以上のみ

        # ルートロガーでログの基本設定を行う - フォーマットとレベル指定があればそれも設定する
        # noinspection PyArgumentList
        basicConfig(
            level       = level or INFO,
            format      = fmt or self._fmt,
            handlers    = [ h1, h2, ],
        )

        # 初期化完了とする
        _Logger     = True

        pass
