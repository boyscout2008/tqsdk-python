# 涵盖现有支持策略，涵盖主流品种
# 铁矿不支持2016年之前的回测，棉花只支持当年的回测
# 所以回归测试尽量安排当年合约回测
# 运行完对比log，看是否正常即可
/d/Anaconda3/python xiadiyu_huice.py --SYMBOL DCE.i1909 --YEAR 2019
/d/Anaconda3/python shuanggui_huice.py --SYMBOL DCE.i1909 --YEAR 2019
/d/Anaconda3/python biyin_huice.py --SYMBOL DCE.i1909 --YEAR 2019 --ZC1 621 --ZC2 571
/d/Anaconda3/python fohuitou_huice.py --SYMBOL DCE.i2001 --YEAR 2020
/d/Anaconda3/python bubugao_huice.py --SYMBOL DCE.i1909 --YEAR 2019

:<<!
2020-03-22 13:26:56,119 - xiadiyu_huice.py[line:97] - INFO: Starting xiadiyu strategy for: DCE.i1909, actually year: 2019
2020-03-22 13:26:58,697 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-03-26, for DCE.i1909, adjust interval: 4
2020-03-22 13:26:58,915 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-03-27, for DCE.i1909, adjust interval: 5
2020-03-22 13:26:59,128 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-03-28, for DCE.i1909, adjust interval: 6
2020-03-22 13:27:02,499 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-04-23, for DCE.i1909, adjust interval: 4
2020-03-22 13:27:02,702 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-04-24, for DCE.i1909, adjust interval: 5
2020-03-22 13:27:02,889 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-04-25, for DCE.i1909, adjust interval: 6
2020-03-22 13:27:03,108 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-04-26, for DCE.i1909, adjust interval: 7
2020-03-22 13:27:08,373 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-06-10, for DCE.i1909, adjust interval: 4
2020-03-22 13:27:20,352 - shuanggui_huice.py[line:90] - INFO: Starting shuanggui strategy for: DCE.i1909, actually year: 2019
2020-03-22 13:27:26,491 - shuanggui_huice.py[line:116] - INFO: MYSTRATEGY - Shuanggui date: 2019-04-22, for DCE.i1909
2020-03-22 13:27:46,642 - biyin_huice.py[line:103] - INFO: Starting biyin strategy for: DCE.i1909, actually year: 2019 with zhicheng1: 621.0, zhicheng2: 571.0
2020-03-22 13:27:53,246 - biyin_huice.py[line:129] - INFO: MYSTRATEGY - biyin date: 2019-04-24, for DCE.i1909
2020-03-22 13:28:14,879 - fohuitou_huice.py[line:91] - INFO: Starting fohuitou strategy for: DCE.i2001, actually year: 2020
2020-03-22 13:28:25,089 - fohuitou_huice.py[line:117] - INFO: MYSTRATEGY - fohuitou_xiaoyin date: 2019-09-17, for DCE.i2001
2020-03-22 13:28:25,948 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-09-23, for DCE.i2001
2020-03-22 13:28:28,691 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-10-15, for DCE.i2001
2020-03-22 13:28:32,451 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-11-05, for DCE.i2001
2020-03-22 13:28:48,745 - bubugao_huice.py[line:90] - INFO: Starting bubugao strategy for: DCE.i1909, actually year: 2019
2020-03-22 13:28:54,297 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-04-12, for DCE.i1909, adjust interval: 4
2020-03-22 13:28:54,641 - bubugao_huice.py[line:118] - INFO: MYSTRATEGY - GOOD BUBUGAO date: 2019-04-15, for DCE.i1909, adjust interval: 5
2020-03-22 13:28:58,381 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-05-13, for DCE.i1909, adjust interval: 4
2020-03-22 13:28:58,823 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-05-15, for DCE.i1909, adjust interval: 6
2020-03-22 13:29:05,575 - bubugao_huice.py[line:118] - INFO: MYSTRATEGY - GOOD BUBUGAO date: 2019-06-27, for DCE.i1909, adjust interval: 5
2020-03-22 13:29:05,794 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-06-28, for DCE.i1909, adjust interval: 6
!