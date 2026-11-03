CREATE TABLE IF NOT EXISTS users(
    id           BIGINT            NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
    username     VARCHAR(50)       NOT NULL                COMMENT '登录名',
    password_hash     VARCHAR(255)   NOT NULL              COMMENT '密码哈希，格式:盐$摘要',
    nickname     VARCHAR(50)       NOT NULL DEFAULT ''     COMMENT '界面显示的昵称',
    avatar       VARCHAR(255)      NOT NULL DEFAULT ''     COMMENT '头像图片的 URL',
    role          VARCHAR(20)  NOT NULL DEFAULT 'employee' COMMENT '角色：employee=员工 admin=管理员',
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username(username)
) ENGINE = InnoDB
    DEFAULT CHARSET = utf8mb4
    COLLATE = utf8mb4_unicode_ci
    COMMENT = '用户表';