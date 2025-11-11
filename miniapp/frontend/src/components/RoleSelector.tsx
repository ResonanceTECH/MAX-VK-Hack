import React from 'react'
import './RoleSelector.css'

interface Role {
  role: string
  fio: string
}

interface RoleSelectorProps {
  roles: Role[]
  currentRole: string
  onRoleChange: (role: string) => void
}

const roleNames: Record<string, string> = {
  admin: 'Администратор',
  support: 'Поддержка',
  teacher: 'Преподаватель',
  student: 'Студент'
}

const RoleSelector: React.FC<RoleSelectorProps> = ({ roles, currentRole, onRoleChange }) => {
  if (roles.length <= 1) {
    return null
  }

  return (
    <div className="role-selector">
      <div className="role-selector-label">Роль:</div>
      <select 
        value={currentRole} 
        onChange={(e) => onRoleChange(e.target.value)}
        className="role-selector-select"
      >
        {roles.map((role) => (
          <option key={role.role} value={role.role}>
            {roleNames[role.role] || role.role} - {role.fio}
          </option>
        ))}
      </select>
    </div>
  )
}

export default RoleSelector

