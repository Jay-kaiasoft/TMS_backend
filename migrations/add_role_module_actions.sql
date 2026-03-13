CREATE TABLE IF NOT EXISTS role_module_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    module_action_id INT NOT NULL,
    UNIQUE KEY unique_rma (role_id, module_action_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (module_action_id) REFERENCES modules_actions(id) ON DELETE CASCADE
);

-- Insert functionality for role management
INSERT IGNORE INTO functionalities (name) VALUES ('manage role');

-- Insert module for role management
INSERT IGNORE INTO modules (functionality_id, name)
  SELECT id, 'Roles List' FROM functionalities WHERE name = 'manage role';

-- Assign all 4 actions to the new module
INSERT IGNORE INTO modules_actions (module_id, action_id)
  SELECT m.id, a.id FROM modules m, actions a WHERE m.name = 'Roles List';
