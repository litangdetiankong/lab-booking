CREATE TABLE IF NOT EXISTS labs (
  id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  name            VARCHAR(100) NOT NULL                COMMENT '实验室名称，唯一',
  description     TEXT                                 COMMENT '详细介绍（阶段三 RAG 也检索它）',
  location        VARCHAR(100) NOT NULL DEFAULT ''     COMMENT '位置，如 A 座 301',
  capacity        INT          NOT NULL DEFAULT 0      COMMENT '可容纳人数',
  open_time_start TIME         NOT NULL                COMMENT '开放开始时刻',
  open_time_end   TIME         NOT NULL                COMMENT '开放结束时刻',
  status          VARCHAR(20)  NOT NULL DEFAULT '开放中' COMMENT '开放中 | 维护中',
  PRIMARY KEY (id),
  UNIQUE KEY uk_labs_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='实验室表';

INSERT INTO labs (name, description, location, capacity, open_time_start, open_time_end, status) VALUES
('AI 实验室',     '配备 8 台 RTX4090 深度学习工作站，支持大模型训练与推理实验', 'A 座 301', 20, '09:00', '21:00', '开放中'),
('机器人实验室',   '两台六轴机械臂与移动机器人平台，支持 ROS2 开发',              'A 座 302', 12, '09:00', '18:00', '开放中'),
('云计算实验室',   'Kubernetes 集群与 GPU 服务器，用于分布式与云原生实验',        'B 座 201', 30, '09:00', '21:00', '开放中'),
('软件工程实验室', '通用开发工位与自动化测试设备',                                'B 座 202', 40, '09:00', '21:00', '开放中'),
('网络实验室',     '路由器、交换机、防火墙全套组网设备',                          'B 座 203', 16, '09:00', '18:00', '维护中');

