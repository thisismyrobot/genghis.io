package genghis.io.android;

import android.os.Bundle;
import android.preference.PreferenceActivity;

/**
 * Created by Bob on 26/07/2014.
 */
public class Preferences extends PreferenceActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        addPreferencesFromResource(R.xml.preferences);
    }
}
