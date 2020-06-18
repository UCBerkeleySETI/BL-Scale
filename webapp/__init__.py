import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bl.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/index')
    @app.route('/')
    def index():
        sample_urls_1 = ['https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/7/214455504.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/7/214455604.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/6/197309688.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/6/197309788.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/9/268371580.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/9/268371680.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/9/272032084.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/9/286709548.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/8/257638320.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/8/258469396.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/8/259749572.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/8/262878500.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/8/262878600.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/136487280.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/136487580.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/137209180.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/137209280.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/138729932.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/138730032.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/141030384.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/4/141030484.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/4204204.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/4215804.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/9402108.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/9402208.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/10450684.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/10450784.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/18306392.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/0/18306492.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/2/80984852.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/2/80984952.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/1/45193468.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58010_50176_HIP61317_fine/filtered/1/45193568.png']

        sample_urls_2 = ['https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195016860.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195067536.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195121936.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195131336.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195137836.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195144636.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195167036.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195171836.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195203636.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195228236.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195237636.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195257736.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195330036.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195357236.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/6/195359236.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/136493080.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/136493180.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/136499780.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/137379356.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/137379456.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/137382256.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/4/141019284.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/2/80767752.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/2/80791752.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/2/80794652.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/2/80809452.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58014_69579_HIP77629_fine/filtered/2/80812152.png']

        sample_urls_3 = ['https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/96300.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/96400.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/375500.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/375600.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/381900.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/382000.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/7164056.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/7164156.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/18317192.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/18317292.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/18382692.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/18382792.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/27049100.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/0/27049200.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/60084332.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/60084432.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/71958968.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/71959068.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/75018296.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/75018396.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/78474724.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/80984852.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/2/80984952.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/1/45193468.png',
 'https://storage.cloud.google.com/bl-scale/GBT_58110_60123_HIP91926_fine/filtered/1/45193568.png']
        # obs_dict = {'GBT_58010_50176_HIP61317_fine': ['10','296909208','296909308','299668860','299668960','299669360'],'GBT_58010_50176_HIP61317_fine':
        # ['223233912','223254312','223274712','223295112']}
        # #obs_names = ['GBT_58010_50176_HIP61317_fine','GBT_58014_69579_HIP77629_fine','GBT_58110_60123_HIP91926_fine','GBT_58202_60970_B0329+54_fine','GBT_58210_37805_HIP103730_fine'
        # #'GBT_58210_39862_HIP105504_fine','GBT_58210_40853_HIP106147_fine','GBT_58210_41185_HIP105761_fine','GBT_58307_26947_J1935+1616_fine','GBT_58452_79191_HIP115687_fine']
        # block_nums = ['0','1','2','3','4','5','6','7','8','9','10']
        # sample_urls_1 = get_img_url(obs_dict, 'GBT_58010_50176_HIP61317_fine')
        #sample_urls_2 = get_img_url(obs_dict, )
        return render_template("index.html", title="Main Page", samples_1=sample_urls_1, samples_2=sample_urls_2, samples_3=sample_urls_3)


    # def get_img_url(obs_dict, dict_key):
    #     url_list = []
    #     for key in obs_dict.keys():
    #         if key==dict_key:
    #             for i in range(1,len(obs_dict[key])):
    #                 url_list += ["https://storage.cloud.google.com/bl-scale/"+key+"/filtered/"+obs_dict[key][0]+"/"+obs_dict[key][i]+".png"]
    #     return url_list


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import monitor
    app.register_blueprint(monitor.bp)

    return app
