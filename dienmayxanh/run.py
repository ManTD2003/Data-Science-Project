from crawl_dmx import crawl_data_multi_threads

urls = ['https://www.dienmayxanh.com/dien-thoai',
        'https://www.dienmayxanh.com/laptop',
        'https://www.dienmayxanh.com/may-tinh-bang',
        'https://www.dienmayxanh.com/dong-ho-thong-minh',
        'https://www.dienmayxanh.com/man-hinh-may-tinh',
        'https://www.dienmayxanh.com/bo-lau-nha',
        'https://www.dienmayxanh.com/noi',
        'https://www.dienmayxanh.com/chao-chong-dinh',
        'https://www.dienmayxanh.com/dao-lam-bep',
        'https://www.dienmayxanh.com/thot',
        'https://www.dienmayxanh.com/tai-nghe',
        'https://www.dienmayxanh.com/sac-cap',
        'https://www.dienmayxanh.com/chuot-may-tinh',
        'https://www.dienmayxanh.com/tui-chong-soc',
        'https://www.dienmayxanh.com/camera-giam-sat',
        'https://www.dienmayxanh.com/usb'
        ]

crawl_data_multi_threads(urls)