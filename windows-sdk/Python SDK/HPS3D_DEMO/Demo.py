import sys
import time
from HPS3D_IF import *

# 申明全局变量
G_DEVICE_ID = 99
G_FPS = 0


# DeBug信息回调函数
def debug_func(message, contex):
    print(message)


# 输出事件回调函数，注意请不要在回调函数中进行耗时较长的操作
def output_event_func(out_id, event, contex):
    global G_FPS
    G_FPS += 1

    if event == EVENT_SIMPLEDISTANCERECVD:  # 简单深度通知事件
        # 简单深度通知事件只能获取数学统计信息
        dict = get_average_distance_cb(out_id)  # 获取平均距离
        if dict['ret_value'] == RET_OK:
            aver_distance = dict['aver_distance']

        dict = get_max_distance_cb(out_id)  # 获取最大距离
        if dict['ret_value'] == RET_OK:
            max_distance = dict['max_distance']

        dict = get_min_distance_cb(out_id)  # 获取最小距离
        if dict['ret_value'] == RET_OK:
            min_distance = dict['min_distance']

        dict = get_valid_average_amplitude_cb(out_id)  # 有效平均幅值，计算不包含0幅值
        if dict['ret_value'] == RET_OK:
            valid_aver_amp = dict['valid_aver_amp']

        dict = get_all_average_amplitude_cb(out_id)  # 平均幅值，计算包含0幅值
        if dict['ret_value'] == RET_OK:
            all_aver_amp = dict['all_aver_amp']

        # 以下为数据显示，实际工程中可删除
        print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
              "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_FULLDISTANCERECVD:  # 完整深度通知事件
        # 完整深度通知事件可以获取数学统计信息和每个像素点的深度值
        dict = get_distance_data_cb(out_id)  # 获取每个像素点的深度数据
        if dict['ret_value'] == RET_OK:
            distance_data = dict['distance_data']

        # 获取深度数据的数数学统计信息
        dict = get_average_distance_cb(out_id)  # 获取平均距离
        if dict['ret_value'] == RET_OK:
            aver_distance = dict['aver_distance']

        dict = get_max_distance_cb(out_id)  # 获取最大距离
        if dict['ret_value'] == RET_OK:
            max_distance = dict['max_distance']

        dict = get_min_distance_cb(out_id)  # 获取最小距离
        if dict['ret_value'] == RET_OK:
            min_distance = dict['min_distance']

        dict = get_valid_average_amplitude_cb(out_id)  # 有效平均幅值，计算不包含0幅值
        if dict['ret_value'] == RET_OK:
            valid_aver_amp = dict['valid_aver_amp']

        dict = get_all_average_amplitude_cb(out_id)  # 平均幅值，计算包含0幅值
        if dict['ret_value'] == RET_OK:
            all_aver_amp = dict['all_aver_amp']

        # 以下为数据显示，实际工程中可删除
        print("中间点距离：%d(MM)" % distance_data[153600])
        print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
              "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_AMPLITUDE:  # 幅值通知事件
        # 幅值通知事件可以获取每个像素点的灰度数据或者幅值数据，以及幅值相关的数学统计信息
        dict = get_grayscale_data_cb(out_id)  # 获取每个像素点的灰度数据，灰度数据由振幅数据归一化处理得到
        if dict['ret_value'] == RET_OK:
            grayscale_data = dict['grayscale_data']

        dict = get_amplitude_data_cb(out_id)  # 获取每个像素点的幅值数据
        if dict['ret_value'] == RET_OK:
            amplitude_data = dict['amplitude_data']

        # 获取振幅相关的数学统计信息
        dict = get_valid_average_amplitude_cb(out_id)  # 获取有效平均幅值
        if dict['ret_value'] == RET_OK:
            valid_aver_amp = dict['valid_aver_amp']

        dict = get_max_amplitude_data_cb(out_id)  # 获取最大幅值
        if dict['ret_value'] == RET_OK:
            max_amplitude = dict['max_amplitude']

        dict = get_min_amplitude_data_cb(out_id)  # 获取最小幅值
        if dict['ret_value'] == RET_OK:
            min_amplitude = dict['min_amplitude']

        # 以下为数据显示，实际工程中可删除
        print("中间点灰度值：%d" % grayscale_data[153600], "中间点幅值：%d" % amplitude_data[153600])
        print("有效平均幅值：%d(MM)" % valid_aver_amp, "最大幅值：%d" % max_amplitude, "最小幅值：%d" % min_amplitude)

    elif event == EVENT_FULLPOINTCLOUDRECVD:  # 完整点云通知事件
        # 完整点云通知事件，能够获取每个像素的点云数据，和深度数据的数学统信息，点云数据自动过滤了无效值
        dict = get_point_cloud_data_cb(out_id)  # 获取每个像素的点云数据
        if dict['ret_value'] == RET_OK:
            point_cloud_data = dict['point_cloud_data']
            point_cloud_count = dict['point_cloud_count']

        # 获取深度相关的数学统计信息
        dict = get_average_distance_cb(out_id)  # 获取平均距离
        if dict['ret_value'] == RET_OK:
            aver_distance = dict['aver_distance']

        dict = get_max_distance_cb(out_id)  # 获取最大距离
        if dict['ret_value'] == RET_OK:
            max_distance = dict['max_distance']

        dict = get_min_distance_cb(out_id)  # 获取最小距离
        if dict['ret_value'] == RET_OK:
            min_distance = dict['min_distance']

        dict = get_valid_average_amplitude_cb(out_id)  # 有效平均幅值，计算不包含0幅值
        if dict['ret_value'] == RET_OK:
            valid_aver_amp = dict['valid_aver_amp']

        dict = get_all_average_amplitude_cb(out_id)  # 平均幅值，计算包含0幅值
        if dict['ret_value'] == RET_OK:
            all_aver_amp = dict['all_aver_amp']

        # 以下为数据显示，实际工程中可删除
        print("最后一个点的坐标:[%.3f, %.3f, %.3f]" % (point_cloud_data[point_cloud_count - 1][0],
                                               point_cloud_data[point_cloud_count - 1][1],
                                               point_cloud_data[point_cloud_count - 1][2]))
        print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
              "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_ROIPOINTCLOUDRECVD:  # ROI点云通知事件
        # ROI点云事件可以获取ROI点云信息和每个ROI的深度数学统计信息
        # 其中获取点云数据有两种方式
        # 第一种，通过点云数据获取接口直接获取点云信息，自动将多个ROI点云数据拼接成
        dict = get_point_cloud_data_cb(out_id)  # 获取每个像素的点云数据
        if dict['ret_value'] == RET_OK:
            point_cloud_data = dict['point_cloud_data']
            point_cloud_count = dict['point_cloud_count']

        # 以下为数据显示，实际工程中可删除
        print("整个点云图最后一个点的坐标:[%.3f, %.3f, %.3f]" % (point_cloud_data[point_cloud_count - 1][0],
                                                    point_cloud_data[point_cloud_count - 1][1],
                                                    point_cloud_data[point_cloud_count - 1][2]))

        # 第二种，获取指定ROI的点云信息
        dict = get_out_roi_param_cb(out_id)  # 获取指定ROI的点云信息前，需要通过ROI参数接口，获取当前输出的ROI信息，（有几个ROI，ROI的ID等）
        if dict['ret_value'] == RET_OK:
            roi_number = dict['roi_number']
            roi_id = dict['roi_id']

            # 依次获取每个ROI值
            for i in range(0, roi_number):
                dict = get_out_roi_point_cloud_data_cb(out_id, roi_id[i])  # 获取指定ROI的点云数据
                if dict['ret_value'] == RET_OK:
                    roi_point_data = dict['roi_point_data']
                    roi_point_count = dict['roi_point_count']

                # 获取指定ROI的深度数据的数学统计信息
                dict = get_out_roi_average_distance_cb(out_id, roi_id[i])  # 获取平均距离
                if dict['ret_value'] == RET_OK:
                    aver_distance = dict['aver_distance']

                dict = get_out_roi_max_distance_cb(out_id, roi_id[i])  # 获取最大距离
                if dict['ret_value'] == RET_OK:
                    max_distance = dict['max_distance']

                dict = get_out_roi_min_distance_cb(out_id, roi_id[i])  # 获取最小距离
                if dict['ret_value'] == RET_OK:
                    min_distance = dict['min_distance']

                dict = get_out_roi_valid_average_amplitude_cb(out_id, roi_id[i])  # 有效平均幅值，计算不包含0幅值
                if dict['ret_value'] == RET_OK:
                    valid_aver_amp = dict['valid_aver_amp']

                dict = get_out_roi_all_average_amplitude_cb(out_id, roi_id[i])  # 平均幅值，计算包含0幅值
                if dict['ret_value'] == RET_OK:
                    all_aver_amp = dict['all_aver_amp']

                # 以下为数据显示，实际工程中可删除
                print("ROI:%d" % roi_id[i])
                print("最后一个点的坐标:[%.3f, %.3f, %.3f]" % (roi_point_data[roi_point_count - 1][0],
                                                       roi_point_data[roi_point_count - 1][1],
                                                       roi_point_data[roi_point_count - 1][2]))
                print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
                      "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_ROIFULLDISTANCERECVD:  # ROI完整深度通知事件
        # ROI完整深度事件，可以获取每个ROI的深度数据和每个ROI的深度数学统计信息
        dict = get_out_roi_param_cb(out_id)  # 获取指定ROI的点云信息前，需要通过ROI参数接口，获取当前输出的ROI信息，（有几个ROI，ROI的ID等）
        if dict['ret_value'] == RET_OK:
            roi_number = dict['roi_number']
            roi_id = dict['roi_id']

            # 依次获取每个ROI值
            for i in range(0, roi_number):
                dict = get_out_roi_distance_data_cb(out_id, roi_id[i])  # 获取指定ROI的深度数据
                if dict['ret_value'] == RET_OK:
                    roi_distance_data = dict['roi_distance_data']
                    roi_pixel_number = dict['roi_pixel_number']

                # 获取指定ROI的深度数据的数学统计信息
                dict = get_out_roi_average_distance_cb(out_id, roi_id[i])  # 获取平均距离
                if dict['ret_value'] == RET_OK:
                    aver_distance = dict['aver_distance']

                dict = get_out_roi_max_distance_cb(out_id, roi_id[i])  # 获取最大距离
                if dict['ret_value'] == RET_OK:
                    max_distance = dict['max_distance']

                dict = get_out_roi_min_distance_cb(out_id, roi_id[i])  # 获取最小距离
                if dict['ret_value'] == RET_OK:
                    min_distance = dict['min_distance']

                dict = get_out_roi_valid_average_amplitude_cb(out_id, roi_id[i])  # 有效平均幅值，计算不包含0幅值
                if dict['ret_value'] == RET_OK:
                    valid_aver_amp = dict['valid_aver_amp']

                dict = get_out_roi_all_average_amplitude_cb(out_id, roi_id[i])  # 平均幅值，计算包含0幅值
                if dict['ret_value'] == RET_OK:
                    all_aver_amp = dict['all_aver_amp']

                # 以下为数据显示，实际工程中可删除
                print("ROI:%d" % roi_id[i])
                print("最后一个点的距离（MM):%d" % roi_distance_data[roi_pixel_number - 1])
                print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
                      "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_ROISIMPLEDISTANCERECVD:  # ROI简单深度通知事件
        # 简单深度事件，可以获取每个ROI的深度数学统计信息
        dict = get_out_roi_param_cb(out_id)  # 获取指定ROI的点云信息前，需要通过ROI参数接口，获取当前输出的ROI信息，（有几个ROI，ROI的ID等）
        if dict['ret_value'] == RET_OK:
            roi_number = dict['roi_number']
            roi_id = dict['roi_id']

            # 依次获取每个ROI值
            for i in range(0, roi_number):
                # 获取指定ROI的深度数据的数学统计信息
                dict = get_out_roi_average_distance_cb(out_id, roi_id[i])  # 获取平均距离
                if dict['ret_value'] == RET_OK:
                    aver_distance = dict['aver_distance']

                dict = get_out_roi_max_distance_cb(out_id, roi_id[i])  # 获取最大距离
                if dict['ret_value'] == RET_OK:
                    max_distance = dict['max_distance']

                dict = get_out_roi_min_distance_cb(out_id, roi_id[i])  # 获取最小距离
                if dict['ret_value'] == RET_OK:
                    min_distance = dict['min_distance']

                dict = get_out_roi_valid_average_amplitude_cb(out_id, roi_id[i])  # 有效平均幅值，计算不包含0幅值
                if dict['ret_value'] == RET_OK:
                    valid_aver_amp = dict['valid_aver_amp']

                dict = get_out_roi_all_average_amplitude_cb(out_id, roi_id[i])  # 平均幅值，计算包含0幅值
                if dict['ret_value'] == RET_OK:
                    all_aver_amp = dict['all_aver_amp']

                # 以下为数据显示，实际工程中可删除
                print("ROI:%d" % roi_id[i])
                print("平均距离：%d(MM)" % aver_distance, "最大距离：%d(MM)" % max_distance, "最小距离：%d(MM)" % min_distance,
                      "有效平均幅值：%d" % valid_aver_amp, "平均幅值：%d" % all_aver_amp)

    elif event == EVENT_DEVDISCONNECT:  # 设备连接中断事件
        print("设备连接中断!")
        # 断开连接,回收资源
        disconnect(out_id)


# 全局声明回调函数
PDEBUGFUNC = CDEBUGFUNC(debug_func)
POUTPUTEVENTFUNC = COUTPUTEVENTFUNC(output_event_func)


def get_device_param():
    """该函数用于获取设备中的一些信息

        注意:
            1.调用前需要确保设备已经正常连接

            2.执行该命令前，需要将运行模式设置为 RUN_IDLE

        """
    global G_DEVICE_ID
    print("------------------------------------------------------------------")

    dict = get_device_sn(G_DEVICE_ID)  # 获取设备序列号
    if dict['ret_value'] != RET_OK:
        print("获取设备序列号失败!")
    else:
        print("设备序列号: %s" % (dict['sn']))

    dict = get_device_version(G_DEVICE_ID)  # 获取设备版本信息
    if dict['ret_value'] != RET_OK:
        print("获取设备版本信息失败!")
    else:
        print("设备版本: 20%d-%d-%d V%d.%d.%d" % (dict['version_year'], dict['version_month'],
                                              dict['version_day'], dict['version_major'], dict['version_minor'],
                                              dict['version_rev']))

    dict = get_sdk_version()  # 获取SDK版本信息
    if dict['ret_value'] != RET_OK:
        print("获取SDK版本信息失败!")
    else:
        print("SDK版本: 20%d-%d-%d V%d.%d.%d" % (dict['version_year'], dict['version_month'],
                                               dict['version_day'], dict['version_major'], dict['version_minor'],
                                               dict['version_rev']))



    dict = get_point_cloud_mode(G_DEVICE_ID)  # 点云模式配置
    if dict['ret_value'] != RET_OK:
        print("获取点云模式配置失败!")
    else:
        print("点云使能: %d, 镜像模式: %d" % (dict['enable'], dict['mode']))

    dict = get_measure_mode(G_DEVICE_ID)  # 获取测量模式
    if dict['ret_value'] != RET_OK:
        print("获取测量模式失败!")
    else:
        print("测量模式: %d" % (dict['mode']))

    dict = get_output_data_type(G_DEVICE_ID)  # 获取输出数据类型
    if dict['ret_value'] != RET_OK:
        print("获取输出数据类型失败!")
    else:
        print("输出数据类型: %d" % (dict['type']))

    dict = get_integ_time(G_DEVICE_ID)  # 获取积分时间
    if dict['ret_value'] != RET_OK:
        print("获取积分时间失败!")
    else:
        print("积分时间: %d" % (dict['time_us']))

    dict = get_roi_group(G_DEVICE_ID)  # 获取当前的ROI组ID
    if dict['ret_value'] != RET_OK:
        print("获取当前的ROI组ID失败!")
    else:
        print("当前的ROI组ID: %d" % (dict['group_id']))

    for i in range(0, 8):
        dict = get_roi_enable(G_DEVICE_ID, i)  # 获取ROI使能
        if dict['ret_value'] != RET_OK:
            print("获取ROI-%d使能失败!" % i)
        else:
            print("ROI-%d使能状态: %d" % (i, dict['enable']))

    dict = get_smooth_filter(G_DEVICE_ID)  # 获取平滑滤波器设置
    if dict['ret_value'] != RET_OK:
        print("获取平滑滤波器设置失败!")
    else:
        print("平滑滤波器类型: %d, 平滑滤波器滤波次数: %d" % (dict['type'], dict['times']))

    dict = get_simple_kalman_filter(G_DEVICE_ID)  # 获取卡尔曼滤波器配置
    if dict['ret_value'] != RET_OK:
        print("获取卡尔曼滤波器配置失败!")
    else:
        print("使能: %d, 比例系数: %d, 阈值检查帧数: %d, 噪声阈值: %d" % (dict['enable'], dict['k'], dict['number'], dict['threshold']))

    dict = get_offset(G_DEVICE_ID)  # 获取距离偏移
    if dict['ret_value'] != RET_OK:
        print("获取距离偏移失败!")
    else:
        print("距离偏移: %d" % (dict['offset_mm']))

    dict = get_run_mode(G_DEVICE_ID)  # 获取当前设备运行模式
    if dict['ret_value'] != RET_OK:
        print("获取运行模式失败!")
    else:
        print("当前运行模式: %d" % dict['run_mode'])

    dict = get_watchdog_enable(G_DEVICE_ID)  # 获取看门狗使能
    if dict['ret_value'] != RET_OK:
        print("获取看门狗使能失败!")
    else:
        print("看门狗使能: %d" % (dict['enable']))


def set_device_param():
    """该函数用于配置设备中的参数

        注意:
            1.调用前需要确保设备已经正常连接

            2.执行该命令前，需要将运行模式设置为 RUN_IDLE

        """
    global G_DEVICE_ID
    # 积分时间根据现场环境和被测物体信号反射强度进行调节（必要）
    dict = set_integ_time(G_DEVICE_ID, 1000)
    if dict['ret_value'] != RET_OK:
        print("设置积分时间失败!")
    else:
        print("设置积分时间成功!")

    # 滤波器配置（可选）
    # 1.平滑滤波器配置, 根据需要自行选择滤波器类型, 以下为关闭
    dict = set_smooth_filter(G_DEVICE_ID, SMOOTH_FILTER_DISABLE, 0)
    if dict['ret_value'] != RET_OK:
        print("设置平滑滤波器失败!")
    else:
        print("设置平滑滤波器成功!")

    # 2.卡尔曼滤波器，根据需要自行选择滤波器参数,以下为关闭
    dict = set_simple_kalman_filter(G_DEVICE_ID, False, 0, 0, 0)
    if dict['ret_value'] != RET_OK:
        print("设置卡尔曼滤波器失败!")
    else:
        print("设置卡尔曼滤波器成功!")

    # 距离偏移（可选），以下默认设置为0
    dict = set_offset(G_DEVICE_ID, 0)
    if dict['ret_value'] != RET_OK:
        print("设置距离偏移失败!")
    else:
        print("设置距离偏移成功!")

    # 将设置保存到用户配置表，保存后重新上电不会丢失
    dict = profile_save_to_user(G_DEVICE_ID)
    if dict['ret_value'] != RET_OK:
        print("用户配置表保存失败!")
    else:
        print("用户配置表保存成功!")

    '''
    # 还原到出厂设置
    dict = profile_restore_factory(G_DEVICE_ID)
    if dict['ret_value'] != RET_OK:
        print("用户配置表保存失败!")
    else:
        print("用户配置表保存成功!")'''


def set_output_type(type_mode):
    """选定一种需要输出的数据，配置完成后将通过回调函数 output_event_func 通知对应事件

        注意:
            1.调用前需要确保设备已经正常连接

            2.执行该命令前，需要将运行模式设置为 RUN_IDLE

            3.每次只能输出一种类型的数据
        参数:
            type_mode: (int)输出数据类型,例如:
                type_mode = 1：简单深度事件

                type_mode = 2：完整深度事件

                type_mode = 3：幅值事件

                type_mode = 4：完整点云事件

                type_mode = 5：ROI点云事件

                type_mode = 6：ROI完整深度事件

                type_mode = 7：ROI简单深度事件

        """
    global G_DEVICE_ID
    if type_mode == 1:  # 设置简单深度事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_SIMPLE)['ret_value'] != RET_OK:
            print("设置简单深度事件失败!");
            return

        # 如果开启了ROI需要关闭，开启了哪个就关闭哪个，以下示例为全部关闭
        for i in range(0, 8):
            if set_roi_enable(G_DEVICE_ID, i, False)['ret_value'] != RET_OK:
                print("设置简单深度事件失败!")
                return

    elif type_mode == 2:  # 设置完整深度事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_FULL)['ret_value'] != RET_OK:
            print("设置完整深度事件失败!");
            return

        # 如果开启了点云转换，则需要关闭
        if set_point_cloud_mode(G_DEVICE_ID, False, MIRROR_DISABLE)['ret_value'] != RET_OK:
            print("设置完整深度事件失败!");
            return

        # 如果开启了ROI需要关闭，开启了哪个就关闭哪个，以下示例为全部关闭
        for i in range(0, 8):
            if set_roi_enable(G_DEVICE_ID, i, False)['ret_value'] != RET_OK:
                print("设置完整深度事件失败!")
                return

    elif type_mode == 3:  # 设置幅值事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_AMPLITUDE)['ret_value'] != RET_OK:
            print("设置幅值事件失败!");
            return

    elif type_mode == 4:  # 设置完整点云事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_FULL)['ret_value'] != RET_OK:
            print("设置完整点云事件失败!");
            return

        # 如果没有开启点云转换，则需要开启
        if set_point_cloud_mode(G_DEVICE_ID, True, MIRROR_DISABLE)['ret_value'] != RET_OK:
            print("设置完整点云事件失败!");
            return

        # 如果开启了ROI需要关闭，开启了哪个就关闭哪个，以下示例为全部关闭
        for i in range(0, 8):
            if set_roi_enable(G_DEVICE_ID, i, False)['ret_value'] != RET_OK:
                print("设置完整点云事件失败!")
                return

    elif type_mode == 5:  # 设置ROI点云事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_FULL)['ret_value'] != RET_OK:
            print("设置ROI点云事件失败!");
            return

        # 如果没有开启点云转换，则需要开启
        if set_point_cloud_mode(G_DEVICE_ID, True, MIRROR_DISABLE)['ret_value'] != RET_OK:
            print("设置ROI点云事件失败!");
            return

        # 如果没有开启ROI需要开启（ROI配置需要使用客户端）SDK仅提供ROI使能开关
        print('以下开启ROI0, 注意如果没有使用客户端绘制ROI区域，设置ROi使能将无效')
        if set_roi_enable(G_DEVICE_ID, 0, True)['ret_value'] != RET_OK:
            print("设置ROI点云事件失败!")
            return

    elif type_mode == 6:  # 设置ROI完整深度事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_FULL)['ret_value'] != RET_OK:
            print("设置ROI完整深度事件失败!");
            return

        # 如果开启了点云转换，则需要关闭
        if set_point_cloud_mode(G_DEVICE_ID, False, MIRROR_DISABLE)['ret_value'] != RET_OK:
            print("设置ROI完整深度事件失败!");
            return

        # 如果没有开启ROI需要开启（ROI配置需要使用客户端）SDK仅提供ROI使能开关
        print('以下开启ROI0, 注意如果没有使用客户端绘制ROI区域，设置ROi使能将无效')
        if set_roi_enable(G_DEVICE_ID, 0, True)['ret_value'] != RET_OK:
            print("设置ROI完整深度事件失败!")
            return

    elif type_mode == 7:  # 设置ROI简单深度事件，需要进行以下配置
        # 设置输出数据类型
        if set_output_data_type(G_DEVICE_ID, OUTPUT_DISTANCE_SIMPLE)['ret_value'] != RET_OK:
            print("设置ROI完整深度事件失败!");
            return

        # 如果没有开启ROI需要开启（ROI配置需要使用客户端）SDK仅提供ROI使能开关
        print('以下开启ROI0, 注意如果没有使用客户端绘制ROI区域，设置ROi使能将无效')
        if set_roi_enable(G_DEVICE_ID, 0, True)['ret_value'] != RET_OK:
            print("设置ROI完整深度事件失败!")
            return

    else:
        print("请参照注释，正确输入参数")
        return

    print("设置输出类型配置成功!")


if __name__ == '__main__':
    # 第一步，注册DeBug信息回调函数，调试时使用，不需要可以不注册（可选）
    if set_debug_callback(PDEBUGFUNC, None)['ret_value'] != RET_OK:
        print("DEBUG信息回调函数注册失败!")
    else:
        print("DEBUG信息回调函数注册成功!")

    # 第二步，连接设备（必要），以下为设备的默认IP和端口号
    dict = connect_by_ethernet("192.168.30.202", 12345)
    if dict['ret_value'] != RET_OK:
        print("设备连接失败，退出程序!")
        # 连接失败，则退出程序
        sys.exit()
    else:
        print("设备连接成功!")
        # 连接成功后将设备ID取出
        G_DEVICE_ID = dict["device_id"]

    # 第三步，注册输出事件回调函数（必要）
    dict = set_output_callback(POUTPUTEVENTFUNC, G_DEVICE_ID, None)
    if dict['ret_value'] != RET_OK:
        print("输出事件回调函数注册失败!")
        # 输出事件回调函数注册失败，则退出程序
        sys.exit()
    else:
        print("输出事件回调函数注册成功!")

    # 第四步，关闭开门狗使能（可选）,调试时使用，调试完成后需要及时开启
    # dict = set_watchdog_enable(G_DEVICE_ID, False);
    # if dict['ret_value'] != RET_OK:
    #    print("看门狗关闭失败!");
    # else:
    #    print("看门狗关闭成功!");

    # 第五步，设备参数配置（可选）, 该部分可以使用客户端配置
    # 首次运行设备时需要配置参数，之后保存到用户配置后再次运行不需要重新配置
    set_device_param()

    # 第六步，设置设备输出类型（必要）
    set_output_type(1)
    print("------------------------------------------------------------------")

    # 第七步，输出数据，可选单次输出一帧数据和连续输出数据两种
    SINGLE = True
    if SINGLE == True:  # 单次测量
        set_run_mode(G_DEVICE_ID, RUN_SINGLE_SHOT)

    else:  # 连续测量
        set_run_mode(G_DEVICE_ID, RUN_CONTINUOUS)

    time.sleep(1)
    print('帧数：%d' % G_FPS)
    G_FPS = 0
    # 停止输出数据
    set_run_mode(G_DEVICE_ID, RUN_IDLE)

    get_device_param()

    # 第八步，断开设备
    disconnect(G_DEVICE_ID)
    print("程序运行完成")
