import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../services/api';

const AdminSettings = () => {
  const [settings, setSettings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await adminAPI.getSettings();
      setSettings(response.data.settings);
    } catch (error) {
      alert('Error loading settings');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSetting = async (key, value) => {
    try {
      await adminAPI.updateSetting(key, { value });
      alert('Setting updated successfully');
      loadSettings();
    } catch (error) {
      alert('Error updating setting');
    }
  };

  const toggleBoolean = (key, currentValue) => {
    const newValue = currentValue === 'true' ? 'false' : 'true';
    handleUpdateSetting(key, newValue);
  };

  return (
    <Layout title="System Settings">
      <div className="space-y-6">
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Global Configuration</h2>
          
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-6">
              {settings.map((setting) => (
                <div key={setting.id} className="border-b border-gray-200 pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{setting.key}</h3>
                      <p className="text-sm text-gray-600 mt-1">{setting.description}</p>
                    </div>
                    <div className="ml-4">
                      {setting.data_type === 'bool' ? (
                        <button
                          onClick={() => toggleBoolean(setting.key, setting.value)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            setting.value === 'true' ? 'bg-blue-600' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              setting.value === 'true' ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      ) : (
                        <input
                          type={setting.data_type === 'int' || setting.data_type === 'float' ? 'number' : 'text'}
                          step={setting.data_type === 'float' ? '0.1' : '1'}
                          defaultValue={setting.value}
                          onBlur={(e) => handleUpdateSetting(setting.key, e.target.value)}
                          className="input-field w-32"
                        />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card bg-yellow-50 border border-yellow-200">
          <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Warning</h3>
          <p className="text-sm text-yellow-800">
            Changing these settings will affect all users globally. Make sure you understand the impact before modifying system configuration.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default AdminSettings;
