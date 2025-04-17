import React, { useState } from 'react';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Button, Form, Input, message } from 'antd';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/user_services/register', {
        username: values.username,
        password: values.password,
        nickname: values.nickname
      });

      if (response.data.user_id) {
        message.success('注册成功');
        navigate('/login');
      }
    } catch (error) {
      message.error(error.response?.data?.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container" 
      style={{ 
        maxWidth: 400,
        margin: '100px auto',
        padding: 24,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        borderRadius: 8
      }}>
      <h2 data-cy="register-title" style={{ textAlign: 'center', marginBottom: 24 }}>
        用户注册
      </h2>
      {/* 新增错误提示容器 */}
      <div data-cy="server-error-message" style={{ color: 'red', marginBottom: 16 }}></div>
      <Form
        name="register"
        onFinish={onFinish}
        data-cy="register-form"
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名!' }]}
        >
          <Input 
            prefix={<UserOutlined />}
            placeholder="用户名"
            data-cy="username-input"
          />
        </Form.Item>

        // 在密码表单项中添加验证规则
        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码!' },
            { 
              validator: (_, value) => 
                /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/.test(value) 
                  ? Promise.resolve() 
                  : Promise.reject('密码必须包含字母、数字和特殊字符')
            }
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码（需包含字母、数字和特殊字符）"
            data-cy="password-input"
          />
        </Form.Item>

        <Form.Item
          name="nickname"
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="昵称（可选）"
            data-cy="nickname-input"
          />
        </Form.Item>

        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            block
            data-cy="submit-button"
          >
            立即注册
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Register;