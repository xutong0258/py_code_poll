# coding=utf-8

from kafka import KafkaProducer, KafkaConsumer
from common.mylogger import my_log

"""定义一个KafkaClient类，封装生产者和消费者的功能"""


class KafkaClient:
    my_log.info("定义一个KafkaClient类，封装生产者和消费者的功能")

    # 初始化方法，接收kafka服务器地址和端口作为一个参数，以及主题作为另一个参数
    def __init__(self, bootstrap_server, topic):
        # 创建一个生产者对象，指定kafka服务器地址和端口
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server)
        # 创建一个消费者对象，指定kafka服务器地址，端口和订阅的主题
        self.consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_server, group_id="zr_test1")
        # 保存主题名称
        self.topic = topic

    # 定义一个方法，用于发送消息到kafka
    def send_message(self, message, timeout=None):
        # 将消息转换为字节串
        message = message.encode('utf-8')
        # 发送消息到指定的主题
        res = self.producer.send(self.topic, message)
        # 返回发送成功的提示
        return res.get(timeout=timeout)

    # 定义一个方法，用于从kafka接收消息，增加一个超时时间作为参数，默认为None,单位是秒
    def receive_message(self, timeout=None, max_records=1, enable_print=True):
        # 从消费者对象中获取消息，如果超时时间不为None，则设置超时时间
        msgs = []
        for records in self.consumer.poll(timeout_ms=timeout * 1000, max_records=max_records).values():
            for record in records:
                msg = record.value.decode("utf8")
                if enable_print:
                   my_log.info(f"kafka返回: offset {record.offset} msg {msg}")
                msgs.append(msg)
        self.consumer.commit()

        return msgs

    def close(self):
        my_log.info("关闭kafka的生产者对象")
        if self.producer:
            self.producer.close()

        my_log.info("关闭kafka的消费者对象")
        if self.consumer:
            self.consumer.commit()
            self.consumer.close()


if __name__ == '__main__':
    client = KafkaClient(bootstrap_server="192.168.2.202:9192", topic="se_voice")

    for msg in client.receive_message(timeout=60 * 1000):
        print(msg)

    for msg in client.receive_message(timeout=60 * 1000):
        print(msg)

    for msg in client.receive_message(timeout=60 * 1000):
        print(msg)

    for msg in client.receive_message(timeout=60 * 1000):
        print(msg)
