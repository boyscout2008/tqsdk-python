# 涵盖现有支持策略，涵盖主流品种
# 铁矿不支持2016年之前的回测，棉花只支持当年的回测
# 所以回归测试尽量安排当年合约回测
# 运行完对比log，看是否正常即可
/d/Anaconda3/python xiadiyu_huice.py --SYMBOL DCE.i1909 --YEAR 2019
/d/Anaconda3/python shuanggui_huice.py --SYMBOL DCE.i1909 --YEAR 2019
/d/Anaconda3/python biyin_huice.py --SYMBOL DCE.i1909 --YEAR 2019 --ZC1 621 --ZC2 571
/d/Anaconda3/python fohuitou_huice.py --SYMBOL DCE.i2001 --YEAR 2020
/d/Anaconda3/python bubugao_huice.py --SYMBOL DCE.i1909 --YEAR 2019
/d/Anaconda3/python dualbo_huice.py --SYMBOL DCE.i2001 --YEAR 2020
/d/Anaconda3/python yiboduo_huice.py --SYMBOL DCE.i2005 --YEAR 2020

:<<!
2020-03-28 22:12:13,177 - xiadiyu_huice.py[line:97] - INFO: Starting xiadiyu strategy for: DCE.i1909, actually year: 2019
2020-03-28 22:12:15,812 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-03-26, for DCE.i1909, adjust interval: 4
2020-03-28 22:12:16,057 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-03-27, for DCE.i1909, adjust interval: 5
2020-03-28 22:12:16,322 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-03-28, for DCE.i1909, adjust interval: 6
2020-03-28 22:12:19,911 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-04-23, for DCE.i1909, adjust interval: 4
2020-03-28 22:12:20,141 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-04-24, for DCE.i1909, adjust interval: 5
2020-03-28 22:12:20,360 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-04-25, for DCE.i1909, adjust interval: 6
2020-03-28 22:12:20,594 - xiadiyu_huice.py[line:123] - INFO: MYSTRATEGY - GOOD XIADIYU date: 2019-04-26, for DCE.i1909, adjust interval: 7
2020-03-28 22:12:26,079 - xiadiyu_huice.py[line:125] - INFO: MYSTRATEGY - NORMAL XIADIYU date: 2019-06-10, for DCE.i1909, adjust interval: 4
2020-03-28 22:12:40,264 - shuanggui_huice.py[line:90] - INFO: Starting shuanggui strategy for: DCE.i1909, actually year: 2019
2020-03-28 22:12:47,371 - shuanggui_huice.py[line:116] - INFO: MYSTRATEGY - Shuanggui date: 2019-04-22, for DCE.i1909
2020-03-28 22:13:10,797 - biyin_huice.py[line:103] - INFO: Starting biyin strategy for: DCE.i1909, actually year: 2019 with zhicheng1: 621.0, zhicheng2: 571.0
2020-03-28 22:13:18,060 - biyin_huice.py[line:129] - INFO: MYSTRATEGY - biyin date: 2019-04-24, for DCE.i1909
2020-03-28 22:13:38,197 - fohuitou_huice.py[line:91] - INFO: Starting fohuitou strategy for: DCE.i2001, actually year: 2020
2020-03-28 22:13:48,636 - fohuitou_huice.py[line:117] - INFO: MYSTRATEGY - fohuitou_xiaoyin date: 2019-09-17, for DCE.i2001
2020-03-28 22:13:49,464 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-09-23, for DCE.i2001
2020-03-28 22:13:51,728 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-10-15, for DCE.i2001
2020-03-28 22:13:54,839 - fohuitou_huice.py[line:119] - INFO: MYSTRATEGY - fohuitou_xiaoyang date: 2019-11-05, for DCE.i2001
2020-03-28 22:14:05,169 - bubugao_huice.py[line:90] - INFO: Starting bubugao strategy for: DCE.i1909, actually year: 2019
2020-03-28 22:14:10,399 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-04-12, for DCE.i1909, adjust interval: 4
2020-03-28 22:14:10,727 - bubugao_huice.py[line:118] - INFO: MYSTRATEGY - GOOD BUBUGAO date: 2019-04-15, for DCE.i1909, adjust interval: 5
2020-03-28 22:14:14,095 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-05-13, for DCE.i1909, adjust interval: 4
2020-03-28 22:14:14,532 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-05-15, for DCE.i1909, adjust interval: 6
2020-03-28 22:14:20,722 - bubugao_huice.py[line:118] - INFO: MYSTRATEGY - GOOD BUBUGAO date: 2019-06-27, for DCE.i1909, adjust interval: 5
2020-03-28 22:14:20,988 - bubugao_huice.py[line:120] - INFO: MYSTRATEGY - NORMAL BUBUGAO date: 2019-06-28, for DCE.i1909, adjust interval: 6
2020-03-28 22:14:30,343 - dualbo_huice.py[line:86] - INFO: Starting dualboduo strategy for: DCE.i2001, actually year: 2020
2020-03-28 22:14:40,149 - dualbo_huice.py[line:111] - INFO: MYSTRATEGY - LIANGBODUO date: 2019-09-12, for DCE.i2001
2020-03-28 22:14:50,051 - dualbo_huice.py[line:111] - INFO: MYSTRATEGY - LIANGBODUO date: 2019-11-25, for DCE.i2001
!