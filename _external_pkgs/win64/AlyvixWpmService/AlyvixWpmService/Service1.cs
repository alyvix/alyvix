/*
Alyvix allows you to automate and monitor all types of applications
Copyright (C) 2016 Alan Pipitone

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
Official website: http://www.alyvix.com/
*/

using System;
using System.Collections.Generic;
using System.Data;
using System.Diagnostics;
using System.ServiceProcess;
using System.Timers;
using Microsoft.Win32;
using System.Data.SQLite;

namespace AlyvixWpmService
{
    public partial class Service1 : ServiceBase
    {
        private static System.Timers.Timer configFileTimer;
        private static System.Timers.Timer wpmTimer;
        private static int polling_frequency = 500; //500 sec
        private static int push_frequency = 2; //2 sec
        private static IniFile iniFile;
        private static List<string> databases;
        private static List<string> databasesMaxAge;

        private static string iniPath;
        public Service1()
        {
            InitializeComponent();
        }

        private string GetIniPath()
        {
            try
            {
                var localmachineKey = Registry.LocalMachine;
                var softwareKey = localmachineKey.OpenSubKey("SOFTWARE");
                var pythonKey = softwareKey.OpenSubKey("Python");
                var pythonCore = pythonKey.OpenSubKey("PythonCore");
                var pythonVer = pythonCore.OpenSubKey("2.7");
                var pythonInstallPath = pythonVer.OpenSubKey("InstallPath").GetValue(null);

                return pythonInstallPath + "\\Lib\\site-packages\\alyvix\\extra\\alyvixservice.ini";
            }
            catch
            {
                return "";
            }

        }

        protected override void OnStart(string[] args)
        {
            try
            {
                iniPath = GetIniPath();

                iniFile = new IniFile(iniPath);
            }
            catch
            {
            }

            try
            {
                databases = iniFile.GetKeys("db_path");
                databasesMaxAge = iniFile.GetKeys("db_max_age");
            }
            catch
            { }

            try
            {
                String polling = iniFile.Read("polling_frequency", "general");
                polling_frequency = Int32.Parse(polling);
            }
            catch
            { }

            try
            {
                String push = iniFile.Read("push_frequency", "general");
                push_frequency = Int32.Parse(push);
            }
            catch
            { }

            // Create a timer with a two second interval.
            configFileTimer = new Timer(polling_frequency * 1000);
            // Hook up the Elapsed event for the timer. 
            configFileTimer.Elapsed += OnTimedConfigFileEvent;
            configFileTimer.AutoReset = true;

            // Create a timer with a two second interval.
            wpmTimer = new Timer();
            wpmTimer.Interval = push_frequency * 1000;
            // Hook up the Elapsed event for the timer. 
            wpmTimer.Elapsed += OnTimedWpmEvent;
            wpmTimer.AutoReset = true;

            configFileTimer.Start();
            wpmTimer.Start();

        }

        protected override void OnStop()
        {
            configFileTimer.Stop();
            wpmTimer.Stop();
        }


        private void OnTimedConfigFileEvent(Object source, ElapsedEventArgs e)
        {
            configFileTimer.Stop();

            try
            {
                databases = iniFile.GetKeys("db_path");
                databasesMaxAge = iniFile.GetKeys("db_max_age");
            }
            catch
            { }

            try
            {
                String polling = iniFile.Read("polling_frequency", "general");
                polling_frequency = Int32.Parse(polling);
            }
            catch
            { }

            try
            {
                String push = iniFile.Read("push_frequency", "general");
                push_frequency = Int32.Parse(push);
            }
            catch
            { }

            configFileTimer.Interval = polling_frequency * 1000;
            wpmTimer.Interval = push_frequency * 1000;
            configFileTimer.Start();

        }

        private static void OnTimedWpmEvent(Object source, ElapsedEventArgs e)
        {
            wpmTimer.Stop();

            try
            {

                for (var i = 0; i < databases.Count; i++)
                {
                    SQLiteConnection m_dbConnection = null;

                    bool isToInsert = true;

                    try
                    {
                        int maxAge = 24;

                        String dbPath = databases[i].Split('=')[1];
                        String testCaseName = databases[i].Split('=')[0];

                        foreach (String maxAges in databasesMaxAge)
                        {
                            try
                            {
                                String testcaseMaxAgeName = maxAges.Split('=')[0];
                                int testcaseMaxAgeValue = Convert.ToInt32(maxAges.Split('=')[1]);

                                if (testcaseMaxAgeName == testCaseName)
                                {
                                    maxAge = testcaseMaxAgeValue;
                                }
                            }
                            catch { }

                        }


                        m_dbConnection =
                            new SQLiteConnection("Data Source=" + dbPath + ";Version=3;");
                        m_dbConnection.Open();

                        //String dbName = Path.GetFileName(dbPath);
                        //dbName = dbName.Split('.')[0];
                        //String dbName = databases[i].Split('=')[0];

                        //check sorting
                        using (SQLiteCommand fmd = m_dbConnection.CreateCommand())
                        {
                            fmd.CommandText = @"SELECT * FROM sorting ORDER BY start_time DESC LIMIT 1;";
                            fmd.CommandType = CommandType.Text;

                            SQLiteDataReader r = null;

                            try
                            {
                                r = fmd.ExecuteReader();
                            }
                            catch
                            {
                                PerformanceCounterCategory.Delete("Alyvix - " + testCaseName);
                            }
                            //r.Read();

                            List<Performance> perfToQuery = new List<Performance>();
                            List<Performance> perfToQueryTimedOut = new List<Performance>();

                            while (r.Read())
                            {
                                for (int j = 0; j < r.FieldCount; j++)
                                {
                                    if (j == 0) continue;

                                    try
                                    {
                                        Performance perf = new Performance();
                                        perf.name = r.GetName(j).Replace("_index", "");
                                        perf.sort = Convert.ToInt32(r[j]);

                                        if (perf.sort == -1)
                                            perfToQueryTimedOut.Add(perf);
                                        else
                                            perfToQuery.Add(perf);
                                    }
                                    catch
                                    {
                                    }

                                }
                                //String a = Convert.ToString(r["perf_1_index"]);
                            }

                            r.Close();

                            perfToQuery.Sort(delegate (Performance p1, Performance p2) {
                                return p1.sort.CompareTo(p2.sort);
                            });

                            List<Performance> SortedList = perfToQuery;
                            SortedList.AddRange(perfToQueryTimedOut);

                            String queryPerfValue = "SELECT start_time";

                            foreach (Performance perf in SortedList)
                            {
                                queryPerfValue = queryPerfValue + ", " + perf.name;
                            }

                            queryPerfValue = queryPerfValue + " FROM runs ORDER BY start_time DESC LIMIT 1;";

                            fmd.CommandText = queryPerfValue;
                            fmd.CommandType = CommandType.Text;
                            r = fmd.ExecuteReader();

                            //r.Read();

                            List<Performance> perfToSend = new List<Performance>();

                            CounterCreationDataCollection ccds = new CounterCreationDataCollection();

                            CounterCreationData counter = new CounterCreationData();
                            counter.CounterName = "Performance Data"; //perf.name;
                            counter.CounterHelp = "performance Data"; //perf.name;
                            counter.CounterType = PerformanceCounterType.NumberOfItems32;

                            ccds.Add(counter);


                            while (r.Read())
                            {
                                for (int j = 0; j < r.FieldCount; j++)
                                {
                                    if (j == 0)
                                    {
                                        // Unix timestamp is seconds past epoch
                                        DateTime dtDateTime = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);
                                        dtDateTime = dtDateTime.AddSeconds(Convert.ToDouble(r[j])).ToLocalTime();

                                        DateTime dateNow = DateTime.Now;

                                        if (dtDateTime < dateNow.AddHours(-maxAge))
                                            isToInsert = false;

                                        continue;  //skip start date
                                    }

                                    try
                                    {
                                        Performance perf = new Performance();
                                        perf.name = r.GetName(j);

                                        try
                                        {
                                            perf.value = Convert.ToDouble(r[j]); // Convert.ToDouble(1000);
                                            //perf.value = Convert.ToInt32(r[j]);
                                        }
                                        catch
                                        {
                                            perf.value = -1;
                                        }

                                        perfToSend.Add(perf);

                                    }
                                    catch
                                    {
                                    }

                                }
                                //String a = Convert.ToString(r["perf_1_index"]);
                            }

                            r.Close();

                            if (isToInsert == false)
                            {
                                try
                                {
                                    PerformanceCounterCategory.Delete("Alyvix - " + testCaseName);
                                }
                                catch
                                { }
                                continue;
                            }


                            bool performanceAreTheSame = true;

                            PerformanceCounterCategory existingAlyCat = new PerformanceCounterCategory("Alyvix - " + testCaseName);

                            try
                            {
                                foreach (string perfcount in existingAlyCat.GetInstanceNames())
                                {
                                    bool perfIsPresent = false;

                                    foreach (Performance perf in perfToSend)
                                    {
                                        if (perf.name == perfcount)
                                            perfIsPresent = true;
                                    }

                                    if (perfIsPresent == false)
                                    {
                                        performanceAreTheSame = false;
                                        break;
                                    }

                                }

                                if (perfToSend.Count != existingAlyCat.GetInstanceNames().Length)
                                {
                                    performanceAreTheSame = false;
                                }
                            }
                            catch
                            {
                                performanceAreTheSame = false;
                            }

                            if (performanceAreTheSame == false)
                            {
                                try
                                {

                                    PerformanceCounterCategory.Delete("Alyvix - " + testCaseName);
                                }
                                catch
                                {

                                }
                            }


                            if (!PerformanceCounterCategory.Exists("Alyvix - " + testCaseName))
                            {

                                try
                                {
                                    PerformanceCounterCategory.Create("Alyvix - " + testCaseName,
                                        "Alyvix - " + testCaseName,
                                        PerformanceCounterCategoryType.MultiInstance,
                                        ccds);

                                    //System.Threading.Thread.Sleep(1000);
                                }
                                catch (Exception ex)
                                {
                                }

                            }


                            foreach (Performance perf in perfToSend)
                            {
                                PerformanceCounter perfCounter = new PerformanceCounter();
                                try
                                {
                                    perfCounter = new PerformanceCounter("Alyvix - " + testCaseName, "Performance Data", perf.name);
                                    perfCounter.ReadOnly = false;
                                    perfCounter.RawValue = (long)perf.value;
                                    //perfCounter.Increment();
                                }
                                catch (Exception ex)
                                {
                                }
                                finally
                                {
                                    perfCounter.Close();
                                }
                            }
                        }

                        m_dbConnection.Close();
                    }
                    catch
                    {

                    }
                    finally
                    {
                        m_dbConnection.Close();
                    }


                }
            }
            catch
            {

            }

            wpmTimer.Start();
        }
    }
}
