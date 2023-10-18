import { Tabs } from 'expo-router';
import Ionicons from 'react-native-vector-icons/Ionicons';

export default () => {
    return (
        <Tabs>
            <Tabs.Screen name="Browse" options={{
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName = focused
                        ? 'compass'
                        : 'compass-outline';
                    return <Ionicons name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#000',
                tabBarInactiveTintColor: 'gray',
                tabBarShowLabel: true,
                headerShown: false,
            }} />
            <Tabs.Screen name="Create" options={{
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName = focused
                        ? 'headset'
                        : 'headset-outline';
                    return <Ionicons name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#000',
                tabBarInactiveTintColor: 'gray',
                tabBarShowLabel: true,
                headerShown: false,
            }} />
            <Tabs.Screen name="Library" options={{
                tabBarIcon: ({ focused, color, size }) => {
                    let iconName = focused
                        ? 'library'
                        : 'library-outline';
                    return <Ionicons name={iconName} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#000',
                tabBarInactiveTintColor: 'gray',
                tabBarShowLabel: true,
                headerShown: false,
            }} />
        </Tabs>
    )
}
