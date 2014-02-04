import allRBAC

C = allRBAC.GeneralHierRBAC()
C.AddUser("mickg")
C.AddUser("zog")
C.AddRole("Backup Operator")
C.AddRole("Restore Operator")
C.AddRole("Grr")
C.AddObject(3);
C.AddObject(2);

C.AddOperation("add")
C.AddOperation("sub")
C.GrantPermission("add",2, "Restore Operator")
C.GrantPermission("add",3, "Backup Operator")
C.GrantPermission("add",3, "Restore Operator")
C.GrantPermission("sub",2, "Backup Operator")
C.AddInheritance("Large Operator","Backup Operator")

C.AssignUser("mickg","Restore Operator")
C.AssignUser("zog","Restore Operator")
C.AssignUser("mickg","Large Operator")

C.CreateSession("mickg","Adder Session",set(["Large Operator"]))
C.CreateSession("zog","Restorer Session",set(["Restore Operator"]))
C.DeleteRole("Grr")
print C.CheckAccess("Adder Session","add",3)
print C.CheckAccess("Restorer Session","sub",3)

