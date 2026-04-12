-- Appt 项目 - PostgreSQL Schema 定义
-- 瑜伽馆预约系统数据库结构

-- =====================================================
-- 表：studios (瑜伽馆信息)
-- =====================================================
CREATE TABLE studios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 表：instructors (教练信息)
-- =====================================================
CREATE TABLE instructors (
    id SERIAL PRIMARY KEY,
    studio_id INT REFERENCES studios(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    avatar_url TEXT,
    description TEXT,          -- 教练简介
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instructors_studio ON instructors(studio_id);
CREATE INDEX idx_instructors_active ON instructors(is_active);

-- =====================================================
-- 表：schedules (排课计划 - 可预约时间段)
-- =====================================================
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    instructor_id INT REFERENCES instructors(id) ON DELETE CASCADE,
    studio_id INT REFERENCES studios(id),
    schedule_date DATE NOT NULL,      -- 日期
    start_time TIME NOT NULL,         -- 开始时间
    end_time TIME NOT NULL,           -- 结束时间
    max_bookings INT DEFAULT 1,       -- 最大预约人数（默认单人课）
    is_recurring BOOLEAN DEFAULT FALSE,  -- 是否重复排课
    recurrence_pattern JSONB,         -- 重复规则（如：每周周一三五）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 防止时间冲突的约束
    CONSTRAINT time_overlap CHECK (end_time > start_time)
);

CREATE INDEX idx_schedules_date ON schedules(schedule_date);
CREATE INDEX idx_schedules_instructor ON schedules(instructor_id);
CREATE INDEX idx_schedules_active ON schedules(is_recurring);

-- =====================================================
-- 表：bookings (预约记录)
-- =====================================================
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    schedule_id INT REFERENCES schedules(id) ON DELETE CASCADE,
    customer_name VARCHAR(50) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed',  -- confirmed/cancelled/no_show
    notes TEXT,                          -- 备注（如：过敏史、特殊需求）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_schedule ON bookings(schedule_id);
CREATE INDEX idx_bookings_customer ON bookings(customer_phone);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_date ON bookings(created_at);

-- =====================================================
-- 表：admins (管理员账号 - 瑜伽馆主)
-- =====================================================
CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    studio_id INT REFERENCES studios(id),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admins_studio ON admins(studio_id);

-- =====================================================
-- 索引优化查询性能 (已在上文定义，这里补充复合索引)
-- =====================================================

-- 快速查询某日期的可用时段
CREATE INDEX idx_schedules_date_time ON schedules(schedule_date, start_time);

-- 快速查询某教练的预约记录
CREATE INDEX idx_bookings_instructor ON bookings(
    schedule_id, 
    (SELECT instructor_id FROM schedules WHERE id = bookings.schedule_id)
);

-- =====================================================
-- 触发器：自动更新 updated_at 时间戳
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 初始化数据 (可选)
-- =====================================================
-- INSERT INTO studios (name, phone, address) VALUES 
-- ('阳光瑜伽馆', '13800138000', '北京市朝阳区某某街道 1 号');

-- INSERT INTO admins (studio_id, username, password_hash) VALUES 
-- (1, 'studio_owner', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S/Q3WjGJl3S3eF');
