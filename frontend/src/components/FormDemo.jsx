import React, { useState } from 'react';

const FormDemo = () => {
  const [formData, setFormData] = useState({
    gender: '',
    hobbies: [],
    country: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form Submitted:', formData);
  };

  return (
    <form 
      data-cy="demo-form"
      onSubmit={handleSubmit}
      style={{ maxWidth: 500, margin: '20px auto', padding: 20 }}
    >
      {/* 单选按钮组 */}
      <div data-cy="gender-group">
        <label>性别：</label>
        <label>
          <input
            type="radio"
            name="gender"
            value="male"
            checked={formData.gender === 'male'}
            onChange={(e) => setFormData({...formData, gender: e.target.value})}
            data-cy="gender-male"
          /> 男性
        </label>
        <label style={{ marginLeft: 15 }}>
          <input
            type="radio"
            name="gender"
            value="female"
            checked={formData.gender === 'female'}
            onChange={(e) => setFormData({...formData, gender: e.target.value})}
            data-cy="gender-female"
          /> 女性
        </label>
      </div>

      {/* 多选框组 */}
      <div data-cy="hobby-group" style={{ marginTop: 15 }}>
        <label>爱好：</label>
        {['music', 'sports', 'reading'].map(hobby => (
          <label key={hobby} style={{ display: 'block', margin: '5px 0' }}>
            <input
              type="checkbox"
              value={hobby}
              checked={formData.hobbies.includes(hobby)}
              onChange={(e) => {
                const hobbies = e.target.checked
                  ? [...formData.hobbies, hobby]
                  : formData.hobbies.filter(h => h !== hobby);
                setFormData({...formData, hobbies});
              }}
              data-cy={`hobby-${hobby}`}
            /> {{
              music: '音乐',
              sports: '运动',
              reading: '阅读'
            }[hobby]}
          </label>
        ))}
      </div>

      {/* 下拉选择框 */}
      <div style={{ marginTop: 15 }}>
        <label>
          国家：
          <select
            value={formData.country}
            onChange={(e) => setFormData({...formData, country: e.target.value})}
            data-cy="country-select"
            style={{ marginLeft: 10, width: 200 }}
          >
            <option value="">请选择</option>
            <option value="cn" data-cy="country-option-cn">中国</option>
            <option value="us" data-cy="country-option-us">美国</option>
            <option value="jp" data-cy="country-option-jp">日本</option>
          </select>
        </label>
      </div>

      <button 
        type="submit"
        style={{ marginTop: 20 }}
        data-cy="submit-button"
      >
        提交
      </button>
    </form>
  );
};

export default FormDemo;